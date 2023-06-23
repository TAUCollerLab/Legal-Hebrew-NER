from results_analysis import lighttag_connection
import multiprocessing as mp
import pandas as pd
import numpy as np
import time
import re


examples = pd.DataFrame(lighttag_connection())  # defining example Dataframe considering the whole data
examples = examples[examples['annotations'].str.len() > 0]  # stay only with annotated paragraphs
relevant_columns = ['example_id', 'tag', 'value', 'start', 'end', 'annotated_by']
final_df = pd.DataFrame()  # initializing a df that will be converted to csv at the end.

for example in range(0, len(examples)):

    annotated_example = pd.json_normalize(examples.iloc[example, :]['annotations'])
    annotated_example = annotated_example[relevant_columns]
    annotated_example = annotated_example.sort_values('end').reset_index(drop=True)  # save order.
    max_annotators = max([len(lis) for lis in annotated_example['annotated_by'].to_list()])
    # handling examples with 1 or 2 annotators:
    column_names = ['annotator_'+str(i) for i in range(1, max_annotators+1)]  # column names start with 1
    annotators_df = pd.DataFrame(annotated_example.pop('annotated_by').to_list(),
                                 columns=column_names)

    annotators_df_copy = annotators_df.copy()
    for col in annotators_df.columns:
        annotators_df_copy[col] = annotators_df[col].apply(
            lambda row: None if (row is None) else row['annotator'])

    concatenation = pd.concat([annotated_example, annotators_df_copy], axis=1)
    final_df = pd.concat([final_df, concatenation], axis=0)


# default is utf-8 and it might be bad encoding on Windows so we add sig:
# final_df.to_csv('annotations.csv', index=False, encoding='utf-8-sig')

final_df = final_df.replace(np.nan, None)

examples['content_words'] = examples['content'].str.split()  # faster than apply method
examples['start_end_tuple'] = examples['content']\
    .apply(lambda row: [(ele.start(), ele.end() - 1) for ele in re.finditer(r'\S+', row)])

examples_copy = examples.copy()
exploded = examples_copy\
    .explode(['content_words', 'start_end_tuple'])\
    .reset_index(drop=True)

exploded = exploded[['example_id', 'content_words', 'start_end_tuple']]
exploded[['start_token', 'end_token']] = pd.DataFrame(exploded['start_end_tuple'].tolist(), index=exploded.index)
exploded['user_1'], exploded['user_2'], exploded['user_3'] = "", "", ""
exploded['content_words'] = exploded['content_words']\
    .apply(lambda row: row if row[-1] not in ['.', ',', '?', '!', ':', ';'] else row[:-1])

# exploded.to_csv('paragraph_words.csv', index=False, encoding='utf-8-sig')
# subset_first_paragraph = exploded.query("example_id == '00afb784-d626-4a58-931e-190f053c3e67'")
# subset_first_annotations = final_df.query("example_id == '00afb784-d626-4a58-931e-190f053c3e67'")
# exploded['annotators'] = np.empty((len(exploded), 0)).tolist()

# final_df['value'] = final_df['value'].str.split()
# final_df.fillna("", inplace=True)
# exploded_final_df = final_df.explode('value').reset_index(drop=True)
# examples['content_words'] = examples['content'].apply(lambda row: row.split())

ids = list(examples['example_id'].unique())


def process_each_paragraph(example_id: str) -> pd.DataFrame:
    """
    :param example_id: first paragraph will be : 00afb784-d626-4a58-931e-190f053c3e67
    :return: dataframe of paragraphs words/tokens and annotations per user.
    """

    subset_first_paragraph = exploded.copy().query("example_id == @example_id")
    subset_first_annotations = final_df.copy().query("example_id == @example_id")

    for word in range(0, len(subset_first_paragraph)):
        last_user = 5  # for the purpose of proper update to word tags and their values.
        for annotation in range(0, len(subset_first_annotations)):
            if subset_first_annotations.iloc[annotation, 3] <= subset_first_paragraph.iloc[word, 3] and subset_first_annotations.iloc[annotation, 4] >= subset_first_paragraph.iloc[word, 4]:
                for user in range(5, 8):
                    if subset_first_annotations.iloc[annotation, user] is not None and last_user < 8:
                        subset_first_paragraph.iloc[word, last_user] = subset_first_annotations.iloc[annotation, 1]
                        last_user += 1

    # dense_df = subset_first_paragraph.copy()
    # dense_df = dense_df[(dense_df['user_3'] != '') |
    #                     (dense_df['user_2'] != '') |
    #                     (dense_df['user_1'] != '')]

    return subset_first_paragraph


# test_try = process_each_paragraph('00cc1fdc-feff-4b90-b5c0-1f1055129d0c')
# test_try = process_each_paragraph('00cc1fdc-feff-4b90-b5c0-1f1055129d0c')  # checking about np.nan


if __name__ == "__main__":

    # results = pd.DataFrame()
    # start_loop = time.time()
    #
    # for id in ids[:200]:
    #     pd.concat([results, process_each_paragraph(id)], axis=0)
    # end_loop = time.time()
    # print("time taken as loop ", end_loop-start_loop)

    start_pool = time.time()
    with mp.Pool(mp.cpu_count()-1) as pool:
        results = pool.map(process_each_paragraph, ids[:])

    output = pd.concat(results, axis=0)
    output.to_csv('sparse_annotations.csv', index=False, encoding='utf-8-sig')

    end_pool = time.time()
    print("time taken with mp: " , end_pool-start_pool)
    # print(results)
    # print(type(results))


#  testing[any([np.where(testing['user_1'].values == '', 0, 1)==1, np.where(testing['user_2'].values == '', 0, 1)==1])]