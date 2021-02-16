def Clean_Characters_by_Dic_(input_directory=""):  # Worksheet에 작업한 내역을 바탕으로 불용어를 처리하는 함수 입니다.

    # 기본적인 아이디어는 1차 Clean_Characters와 같습니다.
    # Read_Sheet를 통해 Worksheet에 접근해서 Clean_Character 컬럼에 1 표시가 된
    # 데이터들의 "tag"열 데이터들을 뽑아옵니다. (제거  대상)
    # 이들을 정규표현식으로 통해 찾아내고, .apply메소드를 통해 제거합니다.
    import os, re
    from tqdm import tqdm
    from .utils import import_dataframe, export_dataframe, Read_Arg_, Read_Sheet_

    tqdm.pandas()

    ref, input_, output_ = Read_Arg_("Clean_Characters_by_Dic")  # Read_Arg를 통해 참조파일, input파일, output파일을 불러옵니다.
    # 이 때 ref는 "Text_PreProcessing_Wokrsheet_Korean"시트를,
    # input파일은 메세지 csv파일의 이름,
    # output은 처리 후 내보낼 메세지 csv파일의 이름입니다.

    JDic = Read_Sheet_(ref)[5:]
    JDic = JDic[~JDic["tag"].duplicated()]
    JDic["unit_length"] = JDic["tag"].apply(lambda x: len(x))
    JDic = JDic.sort_values(by="unit_length", ascending=False)
    JDic_Clean = list(JDic.loc[JDic["Clean_Characters"] == 1, "tag"])
    Clean_candidates = str(JDic_Clean).replace("[", "").replace("]", "").replace(", ''", "").replace(", ", "|").replace("'", "")

    # characters = str(characters).replace("{","").replace("}","").replace(", ''","").replace(", ","|").replace("'","")

    def Clean_stopwords(item):
        item_edited = re.sub(Clean_candidates, " ", item)
        item_edited = re.sub(" +", " ", item_edited)
        return item_edited

    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    input_Message = input_Message[input_Message["contents"].notna()]
    input_Message["contents"] = input_Message["contents"].progress_apply(Clean_stopwords)
    input_Message = input_Message[input_Message["contents"].notna()]
    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)
    return input_Message
