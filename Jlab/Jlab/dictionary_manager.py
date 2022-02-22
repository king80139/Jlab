# 표제화버전 test 백업
def Categorize_Words_With_Dic(username, prname):
    from utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    import pandas as pd
    import os
    from tqdm import tqdm
    import itertools
    tqdm.pandas(desc='사전 업데이트')
    if (username == None) & (prname == None):
        input_directory = ""  # Non-창민버전
    else:
        input_directory = "/".join([username, prname])  # Non-창민버전
    ref, input_, output_ = Read_Arg_(username, prname, "Categorize_Words_With_Dic")
    # 레퍼런스는 기존 딕셔너리 시트(backbone korean sheet)
    # input file은 tag,count 열이 있는 빈도분석 자료

    Lemma_dic = Read_Sheet_(username, prname, 'JDic_Lemmatization(일반lemma사전)')
    Project_dic = Read_Sheet_(username, prname, ref)

    # Project_dic에서 3번째 열부터 끝열까지 가져옵니다.
    # 이후, Replaced_Freqency옆에 category_columns 열을 추가해 Project_dic에서와 같은 형식을 갖도록 합니다.
    input_name = os.path.join(input_directory, input_)
    Replaced_Frequency = import_dataframe(input_name)

    category_columns = Project_dic.columns[2:]
    Expanded_Frequency = pd.concat([Replaced_Frequency, pd.DataFrame(columns=category_columns)], axis=1, sort=True)
    Expanded_Frequency = Expanded_Frequency.drop("Unnamed: 0", axis=1)
    # Expanded_Frequency에 있는 tag중 Project_dic에 있는 tag는 그 정보를 그대로 Expanded_Frequency에 복사해옵니다.
    # 없으면 공란으로 둡니다.
    lemma = Lemma_dic.fillna("").to_numpy(dtype=list)
    all_V = list(map(lambda x: [i for i in x if i != ""], lemma))  # all_V라는 변수에 lemma에 있는 데이터들을 전부 가져옵니다.
    all_V_check = list(itertools.chain(*all_V))

    # 이 때 all_V의 형태는 다음과 같습니다.
    # [[기준단어 a, 변형단어 a-1, 변형단어 a-2,... ],
    #  [기준단어 b, 변형단어 b-1, 변형단어 b-2,... ],
    #  ... ]
    def copy_category_info(item):
        if item in all_V_check:  # 만약 표제화사전 내에 처리할 단어가 존재할 경우
            for k in range(len(all_V)):
                if item in all_V[k]:
                    lemmadf = Project_dic.loc[Project_dic['tag'].isin(
                        all_V[k])]  # 표제화 기준단어와 변형단어를 포함한 list를 찾아내어 해당 list를 tag로 하는 데이터프레임을 생성합니다.
                    if len(lemmadf) == 0:
                        break
                    valuecount = list(map(lambda x: sum(lemmadf.iloc[x] == ''), range(len(lemmadf))))
                    mostvalue = min(valuecount)  # 가장 많은 값이 들어있는 행을 찾아냅니다.
                    index = valuecount.index(mostvalue)
                    Expanded_Frequency.loc[Expanded_Frequency.loc[Expanded_Frequency["tag"] == item].
                                               index, 'Clean_Characters':] = lemmadf.iloc[index,
                                                                             2:].tolist()  # 표제화단어 list에서 가장 많은 값을 가지고 있는 행의 코딩을 복사해 옵니다.

        else:
            if item in list(Project_dic.tag):
                new_info = list(Project_dic.loc[Project_dic["tag"] == item, category_columns].to_dict().values())
                new_info = list(map(lambda x: list(x.values())[0], new_info))
                new_info = list(Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "tag"]) + list(
                    Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "count"]) + new_info
                Expanded_Frequency.loc[Expanded_Frequency.loc[Expanded_Frequency["tag"] == item].index] = new_info
            else:
                new_info = list(Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "tag"]) + list(
                    Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "count"
                    ]) + [""] * len(category_columns)

    output_name = os.path.join(input_directory, output_)
    Expanded_Frequency.tag.progress_apply(copy_category_info)
    # Expanded_Frequency = pd.concat([Project_dic.iloc[0:3], Expanded_Frequency], axis=0, ignore_index=True)
    # 기존 딕셔너리의 설명 행들을 같이 합치는 코드
    export_dataframe(Expanded_Frequency.sort_values(by="count", ascending=False), output_name)


def Update_Dictionary(username,prname):
    """
    기존 딕셔너리와 새 딕셔너리를 합쳐주는 코드입니다.
    ref = 기존 딕셔너리(jlab backbone dictionary의 backbone_korean 시트)
    input = 새 딕셔너리
    output = 합쳐진 딕셔너리
    """
    from utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    import pandas as pd
    import os

    if (username == None) & (prname == None):
        input_directory = ""  # Non-창민버전
    else:
        input_directory = "/".join([username, prname])  # Non-창민버전
    ref, input_, output_ = Read_Arg_(username, prname, "Update_Dictionary")
    input_name = os.path.join(input_directory, input_)
    newDictionary = import_dataframe(input_name)
    oldDictionary = Read_Sheet_(username, prname, ref)

    concatDictionary = pd.concat([oldDictionary, newDictionary])

    duplicated = concatDictionary["tag"].duplicated()
    concatDictionary = concatDictionary[~duplicated].iloc[4:]

    print("df row_remover applied")
    print("removed all duplicated rows")
    function = (lambda x: "" if x == 0 else x)
    concatDictionary = concatDictionary.applymap(function)
    concatDictionary['tag'] = concatDictionary['tag'].astype(str)
    concatDictionary = concatDictionary.sort_values(by='tag').reset_index(drop=True)
    output_name = os.path.join(input_directory, output_)
    export_dataframe(concatDictionary, output_name)