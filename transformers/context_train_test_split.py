from sklearn.model_selection import train_test_split
import pandas as pd

contexts = pd.read_csv('processed_contexts.csv')
train, test = train_test_split(contexts, test_size=0.2)

train.to_csv('contexts_train.csv', index=False)
test.to_csv('context_test.csv', index=False)
