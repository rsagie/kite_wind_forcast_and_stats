from numpy import nan


class CsvFiles:

    @staticmethod
    def write_to_out_file(df, csv_file):
        df.dropna(subset=["timestamp"], inplace=True)
        df.dropna(subset=["wind"], inplace=True)
        df.reset_index(inplace=True)
        df.drop(index = df[(df['wind'] > 40) | (df['wind'] < 0)].index, inplace = True)  # remove invalid values
        df.drop(index = df[(df['gust'] > 40) | (df['gust'] < 0)].index, inplace = True)  # remove invalid values

        df.drop(index = df[(df['timestamp'].dt.hour < 6) | (df['timestamp'].dt.hour > 20)].index, inplace = True)  # remove unrelevant time data
        df.drop(index = df[(df['timestamp'].dt.minute != 0) & (df['timestamp'].dt.minute != 30)].index, inplace = True)  # remove unrelevant time data


        df.rename(columns={'location': ' location', 'wind': ' wind', 'gust': ' gust', 'direction': ' direction',
                           'source': ' source', 'archive_timestamp': ' archive_timestamp'},
                  inplace=True)

        if 'tmp' not in df.columns:
            df['tmp'] = nan  # add tmp 'mock' column

        with open(csv_file, 'a') as f:
            df.to_csv(f, columns=['timestamp', ' location', ' wind', ' gust', ' direction', ' source', ' archive_timestamp', 'tmp'],
                      line_terminator='\n', mode='a', header=f.tell() == 0, index=False)
