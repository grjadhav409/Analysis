import streamlit as st
import pandas as pd
from rdkit import Chem
from rdkit.Chem import BRICS
from rdkit.Chem.Draw import MolsToGridImage
from rdkit.Chem.Draw import MolToImage



# Create a Streamlit app
st.title("Fragment Analysis")

# Upload the dataframe
uploaded_file = st.file_uploader("Upload DataFrame", type=["csv", "xlsx"])

# If a file is uploaded
if uploaded_file is not None:
    try:
        # Read the uploaded file as a dataframe
        df = pd.read_csv(uploaded_file)  # Modify this line accordingly if using an Excel file

        # Display the head of the dataframe
        st.subheader("Uploaded DataFrame")
        st.write(df.head())

        # Get the column names from the dataframe
        column_names = df.columns.tolist()

        # Select the SMILES column
        smiles_column = st.selectbox("Select the SMILES column", column_names)

        # Select the target column
        target_column = st.selectbox("Select the target column", column_names)

        # Find out the number of categories in the target column
        categories = df[target_column].nunique()

        # Create a list to store the fragment analysis results
        fragment_analysis = []

        # Perform fragment analysis for each category
        for category in df[target_column].unique():
            category_df = df[df[target_column] == category]
            category_smiles = category_df[smiles_column]

            # Create a dictionary to store the fragment analysis results for this category
            category_results = {
                'CATEGORY': category,
                'FRAGMENTS': [],
                'FREQUENCY': [],
                'PERCENTAGE': []
            }

            # Calculate fragments for each molecule in the category
            all_frags = []
            for smiles_string in category_smiles:
                mol = Chem.MolFromSmiles(smiles_string)
                if mol is not None:
                    fragments = BRICS.BRICSDecompose(mol)
                    all_frags.extend(fragments)

            # Count the occurrence of each fragment
            fragment_counts = pd.Series(all_frags).value_counts().reset_index()
            fragment_counts.columns = ['FRAGMENTS', 'FREQUENCY']

            # Calculate the percentage of each fragment with respect to the total number of molecules in the category
            total_mols = len(category_smiles)
            fragment_counts['PERCENTAGE'] = (fragment_counts['FREQUENCY'] / total_mols) * 100

            # Store the fragment analysis results for this category
            category_results['FRAGMENTS'] = fragment_counts['FRAGMENTS']
            category_results['FREQUENCY'] = fragment_counts['FREQUENCY']
            category_results['PERCENTAGE'] = fragment_counts['PERCENTAGE']

            # Append the results to the overall fragment analysis list
            fragment_analysis.append(category_results)

        # Generate a separate dataframe for fragment analysis results
        divided_df = pd.concat([pd.DataFrame(category_results) for category_results in fragment_analysis], ignore_index=True)

        # Get unique categories
        categories = divided_df['CATEGORY'].unique()

        # Create a dictionary to store the separate DataFrames for each category
        category_dfs = {}

        # Create separate DataFrames based on categories
        for category in categories:
            category_dfs[category] = divided_df[divided_df['CATEGORY'] == category]

        # Select category
        selected_category = st.selectbox("Select a category", categories)

        if selected_category:
            st.subheader(f"Category: {selected_category}")

           # Display the DataFrame for the selected category
            st.subheader(f"Category: {selected_category}")

            # Create a list of PIL images for the molecules in the dataframe
            images = []
            for i, row in category_dfs[selected_category].iterrows():
                fragment = row['FRAGMENTS']
                mol = Chem.MolFromSmiles(fragment)
                img = MolToImage(mol, size=(100, 100))
                images.append(img)

            # Display the dataframe with images
            st.dataframe(category_dfs[selected_category], image=images, width=800)


    except Exception as e:
        st.error(f"Error occurred: {e}")
