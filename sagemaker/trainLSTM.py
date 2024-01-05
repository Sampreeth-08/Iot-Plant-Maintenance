import argparse
import os
from pandas import read_csv
from datetime import datetime
from math import sqrt
from numpy import concatenate
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from joblib import dump
import numpy
import warnings
import json

warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ =='__main__':

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch_size', type=int, default=72)
    parser.add_argument('--n_train_hours', type=int, default=24*365*2)
    parser.add_argument('--n_validation_hours', type=int, default=24*365*4)

    # input data and model directories
    parser.add_argument('--model_dir', type=str)

    args, _ = parser.parse_known_args()
    
    training_data_directory = os.environ.get('SM_INPUT_DIR') + '/data/training/' 
    model_output_directory = os.environ.get('SM_MODEL_DIR')
    output_data_directory = os.environ.get('SM_OUTPUT_DATA_DIR')
    epochs = args.epochs
    batch_size = args.batch_size
    
    # Read the input dataset
    dataset = read_csv(training_data_directory + 'information.csv', header=0, index_col='date')
    dataset.sort_index(inplace=True)
    dataset = dataset[['pollution', 'dew', 'temp', 'press', 'air', 'sunlight', 'moisture', 'healthy']]
    dataset.drop_duplicates(inplace=True)
    
    # Extract the values from the dataset
    values = dataset.values
    
    # Transform all columns as float
    values = values.astype('float32')

    # Normalize features
    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized_values = scaler.fit_transform(values)
    
    # Convert series to supervised learning
    def transform_to_supervised_series(data, columns, n_in=1, n_out=1, dropnan=True):
        n_vars = 1 if type(data) is list else data.shape[1]
        df = DataFrame(data)
        cols, names = list(), list()
        # input sequence (t-n, ... t-1)
        for i in range(n_in, 0, -1):
            cols.append(df.shift(i))
            names += [('%s(t-%d)' % (columns[j], i)) for j in range(n_vars)]
        # forecast sequence (t, t+1, ... t+n)
        for i in range(0, n_out):
            cols.append(df.shift(-i))
            if i == 0:
                names += [('%s(t)' % (columns[j])) for j in range(n_vars)]
            else:
                names += [('%s(t+%d)' % (columns[j], i)) for j in range(n_vars)]
        # put it all together
        agg = concat(cols, axis=1)
        agg.columns = names
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
        return agg

    # Frame as supervised learning
    supervised_series_dataset = transform_to_supervised_series(normalized_values, dataset.columns, 1, 1)
    supervised_series_dataset.drop(supervised_series_dataset.columns[[9, 10, 11, 12, 13, 14, 15]], axis=1, inplace=True)

    values = supervised_series_dataset.values
    n_train_hours = args.n_train_hours
    n_validation_hours = args.n_validation_hours
    train_data = values[:n_train_hours, :]
    validation_data = values[n_train_hours:n_validation_hours, :]
    
    # Split into input and outputs
    train_X, train_y = train_data[:, :-1], train_data[:, -1]
    validation_X, validation_y = validation_data[:, :-1], validation_data[:, -1]
    # Reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
    validation_X = validation_X.reshape((validation_X.shape[0], 1, validation_X.shape[1]))
    
    # LSTM for time-series predictions
    model = Sequential()
    model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam')

    # Fit the network
    history = model.fit(train_X, train_y, epochs=epochs, batch_size=batch_size, validation_data=(validation_X, validation_y), verbose=2, shuffle=False)

    # Save the model and history to correct directories
    # Save the history
    with open(model_output_directory + '/history.json', 'w') as f:
        json.dump(history.history, f)
    # Save the Scaler
    dump(scaler, model_output_directory + '/scaler.model', protocol=2) 
    # Save the trained model and weights
    model_json = model.to_json()
    with open(model_output_directory + "/model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights(model_output_directory + "/model.h5")
