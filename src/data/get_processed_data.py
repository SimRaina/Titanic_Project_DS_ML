import numpy as np
import pandas as pd
import os

def read_data():
    # set the path of the raw data
    raw_data_path = os.path.join(os.path.pardir, 'data', 'raw')
    train_file_path = os.path.join(raw_data_path, 'train.csv')
    test_file_path = os.path.join(raw_data_path, 'test.csv')
    
    # read the data with all default parameters
    train_df = pd.read_csv(train_file_path, index_col = 'PassengerId')
    test_df = pd.read_csv(test_file_path, index_col = 'PassengerId')
    # create survived column in test_df
    test_df['Survived'] = -888
    # concatenate train_df and test_df
    df = pd.concat((train_df, test_df), axis=0)
    return df

def process_data(df):
    # using the method chaining concept
    return (df
            # 1. Create Title feature
            .assign(Title = lambda x: x.Name.map(get_title)
            # 2. Missing Values
            .pipe(fill_missing_values)
            # 3. Create Fare_Bin features (very low, low, high, very high)
            .assign(Fare_Bin = lambda x: pd.qcut(x.Fare, 4, labels=['very low', 'low', 'high', 'very high']))
            # 4. Create AgeState
            .assign(AgeState = lambda x: np.where(x.Age >= 18, 'Adult', 'Child'))
            # 5. FamilySize
            .assign(FamilySize = lambda x: x.Parch + x.SibSp + 1)
            # 6. IsMother
            .assign(IsMother = lambda x: np.where(((x.Sex == 'female') & (x.Parch > 0) & (x.Age > 18) & (x.Title != 'Miss')), 1, 0))
            # 7. Create Deck
            .assign(Cabin = lambda x: np.where(x.Cabin == 'T', np.nan, x.Cabin))
            .assign(Deck = lambda x: x.Cabin.map(get_deck))
            # 8. Feature Encoding
            .assign(IsMale = lambda x: np.where(x.Sex == 'male', 1, 0))
            .pipe(pd.get_dummies, columns =['Deck', 'Pclass', 'Title', 'Fare_Bin', 'Embarked', 'AgeState'])
            # 9. Drop columns
            .drop(['Cabin', 'Name', 'Ticket', 'Parch', 'SibSb', 'Sex'], axis = 1)
            # 10. Reorder columns
            .pipe(reorder_columns) 
           ) )
            
def get_title(name):
            title_group = { 'mr': 'Mr',
                   'mrs': 'Mrs',
                   'miss': 'Miss',
                   'master': 'Master',
                   'don': 'Sir',
                   'rev': 'Sir',
                   'dr': 'Officer',
                   'mme': 'Mrs',
                   'ms': 'Mrs',
                   'major': 'Officer',
                   'lady': 'Lady',
                   'sir': 'Sir',
                   'mlle': 'Miss',
                   'col': 'Officer',
                   'capt': 'Officer',
                   'the countess': 'Lady',
                   'jonkheer': 'Sir',
                   'dona': 'Lady'                  
                }
            first_name_with_title = name.split(',')[1]
            title = first_name_with_title.split('.')[0]
            title = title.strip().lower()
            return title_group[title]

def get_deck(cabin):
            return np.where(pd.notnull(cabin), str(cabin)[0].upper(), 'Z')

def  fill_missing_values(df):
            # embarked
            df.Embarked.fillna('C', inplace = True)
            # fare
            median_fare = df[(df.Pclass == 3) & (df.Embarked == 'S')]['Fare'].median()
            df.Fare.fillna(median_fare, inplace = True)
            # age
            title_age_median = df.groupby('Title').Age.transform('median')
            df.Age.fillna(title_age_median, inplace = True)
            return df

def reorder_columns(df):
            columns = [column for column in df.columns if column != 'Survived']
            columns = 'Survived' + columns
            df = df[columns]
            return df
            
            
def write_data(df):
            processed_data_path = os.path.join(os.path.pardir, 'data', 'processed')
            write_train_path = os.path.join(processed_data_path, 'train.csv')
            write_test_path = os.path.join(processed_data_path, 'test.csv')
            df[df.Survived != -888].to_csv(write_train_path)
            columns = [column for column in df.columns if column != 'Survived']
            df[df.Survived == -888][columns].to_csv(write_test_path)
            
if __name__ == '__main__':
            df = read_data()
            df = process_data(df)
            write_data(df)
            
