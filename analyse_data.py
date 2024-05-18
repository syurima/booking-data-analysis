import os
import pandas as pd

def load_all(dir):
    dataframes = []
    for filename in os.listdir(dir):
        f = os.path.join(dir, filename)
        # checking if it is a file
        if os.path.isfile(f):
            try: 
                df = (pd.read_csv(f))
                dataframes.append(df)
            except: print(f'couldn\'t read file {f}')
    return pd.concat(dataframes, ignore_index=True)


def main(data_dir):
    df = load_all(data_dir)
    print(df)
    
if __name__ == "__main__":

    data_dir = 'data'
    main(data_dir)