def Categorize_Words_With_Dic(Project_dic, Replaced_Freqency):
    import pandas as pd

    category_columns = Project_dic.columns[2:]
    Expanded_Frequency = pd.concat([Replaced_Freqency, pd.DataFrame(columns=category_columns)], axis=1, sort=True)

    def copy_category_info(item):
        if item in list(Project_dic.tag):
            new_info = list(Project_dic.loc[Project_dic["tag"] == item, category_columns].to_dict().values())
            new_info = list(map(lambda x: list(x.values())[0], new_info))
            new_info = list(Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "tag"]) + list(
                Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "count"]) + new_info
            Expanded_Frequency.loc[Expanded_Frequency.loc[Expanded_Frequency["tag"] == item].index] = new_info
        else:
            new_info = list(Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "tag"]) + list(
                Expanded_Frequency.loc[Expanded_Frequency["tag"] == item, "count"]) + [""] * len(category_columns)

    Expanded_Frequency.tag.apply(copy_category_info)

    return Expanded_Frequency.sort_values(by="count", ascending=False)

def Update_Dictionary(oldDictionary, newDictionary):
    """
    :param oldDictionary: 기존 딕셔너리
    :param newDictionary: 새로 카테고라이징 한 딕셔너리
    :return: oldDictioinary에 newDictionary를 추가한 것 (중복데이터 제거)
    """
    import pandas as pd

    concatDictionary = pd.concat(oldDictionary, newDictionary, axis = 0)
    def nullrow_remover(item):
        values = concatDictionary[concatDictionary["tag"] == item]
        if list(values.values[0][2:24]) == [0] * 22:
            concatDictionary.drop(concatDictionary[concatDictionary["tag"] == item].index.values[0], inplace=True)

        return concatDictionary

    concatDictionary.tag.apply(nullrow_remover)
    duplicated = concatDictionary["tag"].duplicated()
    concatDictionary = concatDictionary[~duplicated]
    #display(df)
    print("df row_remover applied")
    print("removed all duplicated rows")
    function = (lambda x: "" if x == 0 else x)
    concatDictionary = concatDictionary.applymap(function)

    concatDictionary = concatDictionary.sort_values(by=["Replace_Texts", "Clean_Characters", 'Delete_SPAM', 'type',
                            'valence', 'product_attribute', 'interested_in', 'in_search', 'desire',
                            'purchase', 'satisfaction', 'recommendation', 'individuality', 'luxury',
                            'modernity', 'distinction', 'sensibility', 'ethic', 'count', 'tag']).reset_index(drop=True)
    #display(concatDictionary)
    return concatDictionary