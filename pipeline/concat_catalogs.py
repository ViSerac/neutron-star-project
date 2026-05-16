import pandas as pd

def concat_df_atnf():
    df_extragalactic = pd.read_parquet("../data/atnf_processed_extragalactic.parquet")
    df_galactic = pd.read_parquet("../data/atnf_processed_galactic.parquet")
    df_final = pd.concat([df_galactic, df_extragalactic], ignore_index=True)
    df_final.to_parquet("../data/atnf_full.parquet", index=False)  
    
def concat_df_mcgill():
    df_extragalactic = pd.read_parquet("../data/mcgill_processed_extragalactic.parquet")
    df_galactic = pd.read_parquet("../data/mcgill_processed_galactic.parquet")
    df_final = pd.concat([df_galactic, df_extragalactic], ignore_index=True)
    df_final.to_parquet("../data/mcgill_full.parquet", index=False)  

def concat_df_m7_and_cco():
    df_m7 = pd.read_parquet("../data/m7_processed.parquet")
    df_cco = pd.read_parquet("../data/cco_processed.parquet")
    df_final = pd.concat([df_m7, df_cco], ignore_index=True)
    df_final.to_parquet("../data/m7_and_cco_full.parquet", index=False)
        
def concat_all():
    atnf = pd.read_parquet("../data/atnf_full.parquet")
    mcgill = pd.read_parquet("../data/mcgill_full.parquet")
    m7_and_cco = pd.read_parquet("../data/m7_and_cco_full.parquet")
    ns_db = pd.concat([atnf, mcgill, m7_and_cco], ignore_index=True)
    ns_db.to_parquet("../data/NS_db_full.parquet", index=False)
    print("Concat successful")
    
if __name__ == "__main__":
    concat_df_atnf()
    concat_df_mcgill()
    concat_df_m7_and_cco()
    concat_all()