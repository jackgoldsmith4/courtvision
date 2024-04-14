from transformers import BertTokenizerFast, BertForQuestionAnswering
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
import pandas as pd
import torch
import ast

BATCH_SIZE = 8
NUM_EPOCHS = 3
LEARN_RATE = 5e-5

class PlayersDataset(Dataset):
  def __init__(self, dataframe, tokenizer, max_len=512):
    self.dataframe = dataframe
    self.tokenizer = tokenizer
    self.max_len = max_len

  def __len__(self):
    return len(self.dataframe)

  def __getitem__(self, idx):
    row = self.dataframe.iloc[idx]
    question = "Which players in this game log will be in the game recap headline?"
    context = row['context']
    encoding = self.tokenizer.encode_plus(question, context, max_length=self.max_len, truncation=True, padding='max_length', return_tensors='pt', return_offsets_mapping=True)

    # Prepare zero tensors for start and end positions
    start_positions = torch.zeros(self.max_len, dtype=torch.long)
    end_positions = torch.zeros(self.max_len, dtype=torch.long)

    # Access offset mappings
    offset_mapping = encoding['offset_mapping'].numpy()

    # Iterate through spans and adjust start and end token positions
    for start_char, end_char in row['spans']:
      # Initialize token positions as None
      start_token, end_token = None, None

      # Iterate through offset mappings to find token indices
      for i, (offset_start, offset_end) in enumerate(offset_mapping[0]):
        # Find start token index
        if (start_token is None) and (start_char >= offset_start) and (start_char < offset_end):
          start_token = i
        # Find end token index
        if (end_token is None) and (end_char > offset_start) and (end_char <= offset_end):
          end_token = i
          break

      # Update start and end positions if tokens were found
      if start_token is not None and end_token is not None:
        start_positions[start_token] = 1
        end_positions[end_token] = 1

    return {
      'input_ids': encoding['input_ids'],
      'attention_mask': encoding['attention_mask'],
      'start_positions': start_positions,
      'end_positions': end_positions
    }

# Initialize Dataset
train_df = pd.read_csv('contexts_train.csv')
train_df = train_df[['context', 'spans']]
train_df['spans'] = train_df['spans'].apply(ast.literal_eval)

test_df = pd.read_csv('contexts_test.csv')
test_df = test_df[['context', 'spans']]
test_df['spans'] = test_df['spans'].apply(ast.literal_eval)

tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
train_dataset = PlayersDataset(train_df, tokenizer)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_dataset = PlayersDataset(test_df, tokenizer)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=True)

# Initialize model and optimizer
model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
for name, param in model.named_parameters():
  if 'qa_outputs' not in name:
    param.requires_grad = False
optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARN_RATE)

# Train model
model.train()
for epoch in range(NUM_EPOCHS):
  for batch in train_loader:
    optimizer.zero_grad()

    input_ids = batch['input_ids'].squeeze().to(device)
    attention_mask = batch['attention_mask'].squeeze().to(device)
    start_positions = batch['start_positions'].to(device)
    end_positions = batch['end_positions'].to(device)

    outputs = model(input_ids, attention_mask=attention_mask)
    start_logits, end_logits = outputs.start_logits, outputs.end_logits

    # Calculate log likelihoods
    log_likelihoods_start = torch.nn.functional.log_softmax(start_logits, dim=-1)
    log_likelihoods_end = torch.nn.functional.log_softmax(end_logits, dim=-1)

    # Gather the log likelihoods for the actual start and end positions
    actual_start_log_likelihood = log_likelihoods_start.gather(1, start_positions).squeeze(-1)
    actual_end_log_likelihood = log_likelihoods_end.gather(1, end_positions).squeeze(-1)

    # Sum of log likelihoods as loss
    loss = -(actual_start_log_likelihood + actual_end_log_likelihood).mean()

    loss.backward()
    optimizer.step()

# Save model and model weights
torch.save(model.state_dict(), 'model_weights.pth')
torch.save(model, 'full_model.pth')
