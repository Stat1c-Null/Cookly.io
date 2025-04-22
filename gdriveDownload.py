import gdown

#Script to download recipe models and csv file 

url1 = 'https://drive.google.com/uc?id=15SRwfnBqTIRtkUnNlvaz0-ySiXkswtlc'
url2 = 'https://drive.google.com/uc?id=1hgfRKzoo0--c3sSK-Ab1_bLW2AxC0xfS'
# Or use the full share link:
# url = 'https://drive.google.com/file/d/FILE_ID/view?usp=sharing'

# Download the file
output = 'SBertModel.pt'  # Desired local filename
gdown.download(url1, output, quiet=False)

output = 'RecipeNLG_enriched.csv'  # Desired local filename
gdown.download(url2, output, quiet=False)