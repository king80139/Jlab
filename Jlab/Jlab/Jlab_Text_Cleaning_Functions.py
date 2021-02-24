def Delete_Messages(input_directory=""):
    # SPAM 메세지라고 판단할 수 있는 요소를 찾아 데이터 제거하는 함수
    # 기본적인 아이디어는 1차 Lemmatization함수와 같습니다.
    # Read_Sheet를 통해 SPAM사전에 접근한 뒤,
    # SPAM이라고 판단할 수 있는 표현이 있는 메세지들을
    # .apply메소드를 통해 제거합니다.
    import os, re
    from tqdm import tqdm
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe

    tqdm.pandas()

    ref, input_, output_ = Read_Arg_("Delete_Messages")

    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    input_Message = input_Message[input_Message["contents"].notna()]

    SPAM = list(Read_Sheet_(ref).iloc[:, 0])
    SPAM = str(SPAM).replace("[", "").replace("]", "").replace(", ''", "").replace(", ", "|").replace("'", "")
    SPAM = re.compile(SPAM)

    input_Message["SPAM"] = input_Message["contents"].progress_apply(SPAM.search)
    input_Message = input_Message[input_Message["SPAM"].isna()].drop(["SPAM"], axis = 'columns')

    input_Message.sort_values(by="date", inplace=True)
    input_Message.reset_index(drop=True, inplace=True)

    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)

    return input_Message

########################################################################################################################

def Delete_Overlapped_Messages(input_directory=""):  # 중복메세지를 제거하는 함수입니다.
    import os
    from tqdm import tqdm
    from .utils import Read_Arg_, import_dataframe, export_dataframe
    tqdm.pandas()

    ref, input_, output_ = Read_Arg_("Delete_Overlapped_Messages")  # Read_Arg를 통해 참조파일, input파일, output파일을 불러옵니다.
    # 이 때 ref는 Overlapped여부를 판가름하는 문자열의 길이,
    # input파일은 메세지 csv파일의 이름,
    # output은 처리 후 내보낼 메세지 csv파일의 이름입니다.

    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    # input_Message의 contents 열에서 결측치를 제외한 데이터들만을 가져옵니다.
    input_Message = input_Message[input_Message["contents"].notna()]
    input_Message.sort_values(by="contents", inplace=True)  # contents열을 기준으로 정렬해줍니다.
    input_Message.reset_index(drop=True, inplace=True)  # 데이터프레임의 index를 새로 정리합니다.

    input_Message["contents_til_" + str(ref)] = input_Message["contents"].progress_apply(
        lambda x: x[:ref] if len(x) >= ref else x)
    # 메세지 데이터 한 행의 데이터의 길이가 ref보다 길면 ref만큼을 가져오고,
    # 짧으면 그 데이터를 그대로 가져오는 함수를 .apply메소드를 통해
    # input_Message의 contents열에 적용시키고,
    # 그 결과값을 input_Message의 contents_til_...이라는 새로운 컬럼을 만들고 표시합니다.
    input_Message = input_Message[
        ~input_Message["contents_til_" + str(ref)].duplicated()].drop(
        ["contents_til_" + str(ref)], axis = 'columns')
    # input_Message의 contents_til_...이라는 컬럼을 기준으로
    # 중복되지 않은(~)데이터들만을 뽑아 (중복메세지 제거)
    # date, contents 열만 살려 input_Message변수를 업데이트 시켜줍니다.

    input_Message.sort_values(by="date", inplace=True)  # date 기준으로 데이터를 정렬하고
    input_Message.reset_index(drop=True, inplace=True)  # index를 재설정해줍니다.

    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)  # 설정한 input_directory에 output 파일을 저장하고

    return input_Message  # 이 함수의 리턴값으로 처리된 input_Message를 내보냅니다. (DataFrame형식)

########################################################################################################################

def Delete_StandardStopwords(input_directory = ""):  # 1차 불용어 처리 (불용어 사전을 새로 수정하고 만들어야 합니다.)
    import re, os
    from tqdm import tqdm
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    tqdm.pandas()

    ref, input_, output_ = Read_Arg_("Delete_StandardStopwords")  # Read_Arg를 통해 참조파일, input파일, output파일을 불러옵니다.
    # 이 때 ref는 "JDic_BizStopwords(경영불용어사전)"시트를,
    # input파일은 메세지 csv파일의 이름,
    # output은 처리 후 내보낼 메세지 csv파일의 이름입니다.

    Clean = Read_Sheet_(ref)  # Clean이라는 변수에 Read_Sheet를 통해
    # "JDic_BizStopwords(경영불용어사전)"시트를 불러옵니다.
    Clean.columns = Clean.iloc[0]
    Clean = Clean[1:]
    Clean["unit_length"] = Clean["word"].apply(lambda x: len(x))  # 이 때 하나의 이슈는 표현의 길이에 따른 나열 순서입니다.
    # (https://greeksharifa.github.io/정규표현식(re)/2018/07/22/regex-usage-03-basic/)
    # 만약 "에게"와 "에게서"를 예시로 들 떄,
    # 정규식 인자로 "에게"가 "에게서"보다 먼저 나열될 경우,
    # 메세지에서 "에게"에 대한 데이터를 먼저 찾으므로
    # 실제로 메세지에서 "에게서" 라고 표현되었던 데이터가
    # "에게"로 인해 "서"만으로 남게됩니다.
    # 따라서 위 방법을 사용하게 될 경우,
    # 불용어 사전의 칼럼으로 unit_length를 두고
    # 내림차순으로 정렬하는 것이 바람직해 보입니다.
    Clean = Clean.sort_values(by="unit_length", ascending=False)  # unit_length열 기준으로 내림차순으로 정렬해주고 최신화합니다.
    Clean = Clean[~Clean["word"].duplicated()]  # 혹시모를 중복 word를 제거합니다.

    symbol = set(Clean.loc[Clean["class"] == "s", "word"])  # 기호는 Clean 데이터 프레임에서
    # "class" 컬럼이 s인 것들의 "word"컬럼을 리스트화한 것입니다.
    symbol = str(symbol).replace("{", "").replace("}", "").replace(", ''", "").replace(", ", "|").replace("'", "")

    # print(symbol)

    characters = set(Clean.loc[Clean["class"] == "c", "word"])  # 문자는 Clean 데이터 프레임에서
    # "class" 컬럼이 c인 것들의 "word"컬럼을 리스트화한 것입니다.
    characters = str(characters).replace("{", "").replace("}", "").replace(", ''", "").replace(", ", "|").replace("'", "")


    # 정규표현식을 사용하기 위한 작업입니다.
    # 본디, JDic_Clean은 ["물론", "무엇", "무슨" …] 처럼 리스트의 형태를 취합니다.
    # 정규표현식을 조작하게끔 하는 라이브러리 re는 인자로 문자열을 받습니다.
    # 따라서 리스트를 문자열로 바꿔줍니다. ( str(JDic_Clean) )
    # 또한, 정규식에는 .sub 메소드가 있는데,
    # 이는 세번째 인자(데이터)에서 첫번째 인자(특정 표현)를 발견하면
    # 두번째 인자로 바꿔주는 메소드입니다.
    # 아래에서 item(메세지 데이터의  각 행에 해당하는 데이터) 데이터에서
    # 불용어사전에 등록된 표현을 찾아 공백으로 바꿔주고자 합니다.
    # 이 때, 불용어 사전에 등록된 단어를 하나하나 바꿔주기 보다,
    # or식( | )을 써서 한번에 lookup하고자 합니다.
    # 그러기 위해서는 정규식의 인자에 들어가야할 형태는 다음과 같습니다.
    # "표현 1"|"표현 2"|"표현3"|…"
    # 더욱이 "ㅜ" 같은경우 "ㅜㅜ"로 메세지에서 발견될 수 있습니다.
    # 이는 정규식 내 +를 넣어주면 해결됩니다.
    # +는 해당표현이 1번이상 반복되는 경우를 뜻합니다.
    # 해당표현 바로 뒤에 +를 써줘 정규식에 넣어줘야 합니다.
    # 따라서 위 Clean_Candidates에는 다음과 같이 형태가 이루어져 있습니다.
    # "표현 1 +"|"표현 2 +"|"표현 3 +"|...

    def Clean_symbol(item):  # Clean_stopwords라는 사용자정의함수를 정의합니다.
        item_edited = re.sub(symbol, " ", item)  # 이는 정규표현식을 통해 item(input_Message의 각행의 데이터)에 대해
        # Clean_candidates에 해당하는 패턴이 나올 시 " "(공백)으로 치환해주는 함수입니다.
        item_edited = " ".join(item_edited.split())  # 다중공백도 제거해줍니다.
        return item_edited  # 이 함수의 리턴값을 치환된 데이터로 최신화된 데이터로 내보내도록 합니다.

    # def add_space_for_symbol(item):
    #    not_words = list(filter(bool, list(set(re.compile("[^\s*\w*\s*]*").findall(item)))))
    #    for end in not_words:                                     # 메세지의 한 행에서 있는 not_words리스트 요소마다
    #        item = item.replace(end," "+end)                                    # replace메소드를 통해 스페이스를 첨가해줍니다.
    #    return item

    def Clean_char(item):  # Clean_stopwords라는 사용자정의함수를 정의합니다.

        item_edited = re.sub(characters, " ", item)  # 이는 정규표현식을 통해 item(input_Message의 각행의 데이터)에 대해
        # Clean_candidates에 해당하는 패턴이 나올 시 " "(공백)으로 치환해주는 함수입니다.
        item_edited = " ".join(item_edited.split()) # 다중공백도 제거해줍니다.
        return item_edited  # 이 함수의 리턴값을 치환된 데이터로 최신화된 데이터로 내보내도록 합니다.

    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    input_Message = input_Message[input_Message["contents"].notna()]  # input Message에 있을 결측치(빈칸)을 제거합니다.
    input_Message["contents"] = input_Message["contents"].progress_apply(Clean_symbol)
    # Clean_stopwords를 .apply메소드를 통해 적용시킵니다.
    # input_Message["contents"] = input_Message["contents"].progress_apply(add_space_for_symbol) #살릴 기호들 앞에 스페이스를 첨가해줍니다.
    input_Message["contents"] = input_Message["contents"].progress_apply(Clean_char)
    # Clean_stopwords를 .apply메소드를 통해 적용시킵니다.

    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)

    return input_Message  # Delete_Characters의 리턴값으로 최신화된 데이터프레임으로 내보내도록 합니다.

########################################################################################################################

def Replace_Texts_in_Messages(input_directory = ""):  # 1차 Lemmatization 함수
    # (지금은 "JDic_Lemmatization(일반lemma사전)"의 양이 적어 이렇게 가지만,
    # 양이 많아진다면 2차 Lemmatization 함수처럼 수정해야 합니다.)
    import os
    from tqdm import tqdm
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    from flashtext import KeywordProcessor
    tqdm.pandas()

    kp = KeywordProcessor()
    ref, input_, output_ = Read_Arg_("Replace_Texts_in_Messages")  # Read_Arg를 통해 참조파일, input파일, output파일을 불러옵니다.
    # 이 때 ref는 "JDic_Lemmatization(일반lemma사전)"시트를,
    # input파일은 메세지 csv파일의 이름,
    # output은 처리 후 내보낼 메세지 csv파일의 이름입니다.

    # lemma라는 변수에 reference 시트를 불러오기
    lemma = Read_Sheet_(ref)  # lemma라는 변수에 Read_Sheet를 통해
    # "JDic_Lemmatization(일반lemma사전)"시트를 불러옵니다.
    lemma = lemma.fillna("").to_numpy(dtype=list)
    all_V = list(map(lambda x: [i for i in x if i != ""], lemma))  # all_V라는 변수에 lemma에 있는 데이터들을 전부 가져옵니다.

    # 이 때 all_V의 형태는 다음과 같습니다.
    # [[기준단어 a, 변형단어 a-1, 변형단어 a-2,... ],
    #  [기준단어 b, 변형단어 b-1, 변형단어 b-2,... ],
    #  ... ]
    for case in all_V:
        standardised = case[0]
        for keyword in case[1:]:
            kp.add_keyword(keyword, standardised)

    def lemmatize(item):  # lemmatize라는 함수를 정의합니다.
        return kp.replace_keywords(item)
        # item_edited = item
        # for case in all_V:  # all_V내에 있는 단어세트(case) (ex. [기준단어 a, 변형단어 a-1, 변형단어 a-2,... ])별로
        #     exp4re = str(sorted(case[1:], key=len, reverse=True)).replace("[", "").replace("]",
        #                 "").replace(", ''", "").replace(", ", "|").replace("'", "")
        #     # [변형단어 a-1, 변형단어 a-2,... ]로 있는 case[1:]라는 리스트를 문자열로 바꿔주고,
        #     # "변형단어 a-1 +|변형단어 a-2 +|..." 식으로 바꿔줍니다.
        #     # 이는 정규식을 사용하기 위한 전처리 작업입니다.
        #     # 정규표현식을 사용하면 원하는 패턴의 문자열을 한번에 찾고 한번에 바꿀 수 있습니다.
        #     item_edited = re.sub(exp4re, case[0], item_edited)  # 변형단어들을 기준단어로 치환해주고 이를 item_edited라는 변수에 넣어줍니다.
        #     item_edited = re.sub("[\s]+", " ", item_edited)  # item_edited의 다중공백(space 두 개 이상의 공백)을 하나의 space로 치환합니다.
        # return item_edited  # item_edited을 리턴값으로 내보냅니다.


    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    input_Message["contents"] = input_Message["contents"].progress_apply(lemmatize)  # lemmatize함수를 .apply메소드를 통해
    # input_Message의 "contents"열에 적용시키고 표시합니다.

    input_Message = input_Message[input_Message["contents"].notna()]  # Null 값이 아닌 데이터들만을 표시합니다.
    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)

    return input_Message  # 처리한 input_Message를 리턴값으로 내보냅니다.

########################################################################################################################

def Delete_Characters(input_directory = ""):  # 1차 불용어 처리 (불용어 사전을 새로 수정하고 만들어야 합니다.)
    import re, os
    from tqdm import tqdm
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    tqdm.pandas()

    ref, input_, output_ = Read_Arg_("Delete_Characters")  # Read_Arg를 통해 참조파일, input파일, output파일을 불러옵니다.
    # 이 때 ref는 "Project_Stopwords"시트를,
    # input파일은 메세지 csv파일의 이름,
    # output은 처리 후 내보낼 메세지 csv파일의 이름입니다.

    Clean = Read_Sheet_(ref)  # Clean이라는 변수에 Read_Sheet를 통해
    # "JDic_BizStopwords(경영불용어사전)"시트를 불러옵니다.
    Clean.columns = Clean.iloc[0]
    Clean = Clean[1:]
    Clean["unit_length"] = Clean["word"].apply(lambda x: len(str(x)))  # 이 때 하나의 이슈는 표현의 길이에 따른 나열 순서입니다.
    # (https://greeksharifa.github.io/정규표현식(re)/2018/07/22/regex-usage-03-basic/)
    # 만약 "에게"와 "에게서"를 예시로 들 떄,
    # 정규식 인자로 "에게"가 "에게서"보다 먼저 나열될 경우,
    # 메세지에서 "에게"에 대한 데이터를 먼저 찾으므로
    # 실제로 메세지에서 "에게서" 라고 표현되었던 데이터가
    # "에게"로 인해 "서"만으로 남게됩니다.
    # 따라서 위 방법을 사용하게 될 경우,
    # 불용어 사전의 칼럼으로 unit_length를 두고
    # 내림차순으로 정렬하는 것이 바람직해 보입니다.
    Clean = Clean.sort_values(by="unit_length", ascending=False)  # unit_length열 기준으로 내림차순으로 정렬해주고 최신화합니다.
    Clean = Clean[~Clean["word"].duplicated()]  # 혹시모를 중복 word를 제거합니다.
    column_data = list(Clean["word"])  # columns_data에 word열에 있는 데이터를 리스트로 변환합니다.
    Clean_cadidates = str(column_data).replace("[", "").replace("]", "").replace(", ''", "").replace(", ", "|").replace(
        "'", "")

    # 정규표현식을 사용하기 위한 작업입니다.
    # 본디, JDic_Clean은 ["물론", "무엇", "무슨" …] 처럼 리스트의 형태를 취합니다.
    # 정규표현식을 조작하게끔 하는 라이브러리 re는 인자로 문자열을 받습니다.
    # 따라서 리스트를 문자열로 바꿔줍니다. ( str(JDic_Clean) )
    # 또한, 정규식에는 .sub 메소드가 있는데,
    # 이는 세번째 인자(데이터)에서 첫번째 인자(특정 표현)를 발견하면
    # 두번째 인자로 바꿔주는 메소드입니다.
    # 아래에서 item(메세지 데이터의  각 행에 해당하는 데이터) 데이터에서
    # 불용어사전에 등록된 표현을 찾아 공백으로 바꿔주고자 합니다.
    # 이 때, 불용어 사전에 등록된 단어를 하나하나 바꿔주기 보다,
    # or식( | )을 써서 한번에 lookup하고자 합니다.
    # 그러기 위해서는 정규식의 인자에 들어가야할 형태는 다음과 같습니다.
    # "표현 1"|"표현 2"|"표현3"|…"
    # 더욱이 "ㅜ" 같은경우 "ㅜㅜ"로 메세지에서 발견될 수 있습니다.
    # 이는 정규식 내 +를 넣어주면 해결됩니다.
    # +는 해당표현이 1번이상 반복되는 경우를 뜻합니다.
    # 해당표현 바로 뒤에 +를 써줘 정규식에 넣어줘야 합니다.
    # 따라서 위 Clean_Candidates에는 다음과 같이 형태가 이루어져 있습니다.
    # "표현 1 +"|"표현 2 +"|"표현 3 +"|...

    def Clean_stopwords(item):  # Clean_stopwords라는 사용자정의함수를 정의합니다.
        item_edited = re.sub(Clean_cadidates, " ", item)  # 이는 정규표현식을 통해 item(input_Message의 각행의 데이터)에 대해
        # Clean_candidates에 해당하는 패턴이 나올 시 " "(공백)으로 치환해주는 함수입니다.
        item_edited = re.sub(" +", " ", item_edited)  # 다중공백도 제거해줍니다.
        return item_edited  # 이 함수의 리턴값을 치환된 데이터로 최신화된 데이터로 내보내도록 합니다.

    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    input_Message = input_Message[input_Message["contents"].notna()]  # input Message에 있을 결측치(빈칸)을 제거합니다.
    input_Message["contents"] = input_Message["contents"].progress_apply(
        Clean_stopwords)  # Clean_stopwords를 .apply메소드를 통해 적용시킵니다.

    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)
    return input_Message  # Delete_Characters의 리턴값으로 최신화된 데이터프레임으로 내보내도록 합니다.

########################################################################################################################

def Delete_Characters_by_Dic(input_directory = ""):  # Worksheet에 작업한 내역을 바탕으로 불용어를 처리하는 함수 입니다.

    # 기본적인 아이디어는 1차 Delete_Characters와 같습니다.
    # Read_Sheet를 통해 Worksheet에 접근해서 Clean_Character 컬럼에 1 표시가 된
    # 데이터들의 "tag"열 데이터들을 뽑아옵니다. (제거  대상)
    # 이들을 정규표현식으로 통해 찾아내고, .apply메소드를 통해 제거합니다.
    import os, re
    from tqdm import tqdm
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    tqdm.pandas()

    ref, input_, output_ = Read_Arg_("Delete_Characters_by_Dic")  # Read_Arg를 통해 참조파일, input파일, output파일을 불러옵니다.
    # 이 때 ref는 "Text_PreProcessing_Wokrsheet_Korean"시트를,
    # input파일은 메세지 csv파일의 이름,
    # output은 처리 후 내보낼 메세지 csv파일의 이름입니다.

    JDic = Read_Sheet_(ref)[5:]
    JDic = JDic[~JDic["tag"].duplicated()]
    JDic["unit_length"] = JDic["tag"].apply(lambda x: len(str(x)))
    JDic = JDic.sort_values(by="unit_length", ascending=False)
    JDic_Clean = list(JDic.loc[JDic["Delete_Characters"] == 1, "tag"])
    Clean_candidates = str(JDic_Clean).replace("[", "").replace("]", "").replace(", ''", "").replace(", ", "|").replace("'",
                                                                                                                        "")

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

########################################################################################################################

def Replace_Texts_by_Dic(input_directory = ""):  # 2차 Lemmatization하는 함수입니다.
    import os
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    from tqdm import tqdm
    tqdm.pandas()  # 진행상황과 예정 ETA를 알려주는 tqdm 라이브러리 중,
    # apply 메소드에 적용되는 .pandas() 명령문을 실행해줍니다. (apply는 밑에 나옵니다.)

    ref, input_, output_ = Read_Arg_(
        "Replace_Texts_by_Dic")  # Read_Arg 명령문을 통해 Jlab Library에 해당 명령문에 필요한 참조파일, 인풋, 아웃풋을 가져옵니다.

    Dls = Read_Sheet_(ref)[5:]
    Dls = Dls[Dls["Replace_Texts"] != ""]  # Replace_Texts에 뭐라도 써있는 것들만으로 범위를 줄여줍니다.
    Dls = Dls[["tag", "Replace_Texts"]]  # Worksheet 중 tag와 Replace_Texts에만 해당하는 컬럼만으로 줄여줍니다.
    Dls = Dls[~Dls.duplicated()].reset_index(drop=True)  # 중복된 것들을 제거해준 뒤, index를 새로 만들어줍니다.

    # 이 아래부터의 방식은 apply 방식을 위한 작업입니다.
    # 밑의 .apply메소드는 판다스 데이터프레임의 행마다 접근해 차례대로 정의한 함수를 실행시키는 방법입니다.
    # 현재 나와있는 pandas 처리 방법 중에 가장 빠른 속도를 보이는 메소드 입니다.

    def lemmatize(item):  # lemmatize라는 함수를 사용자 정의 함수로 정의 합니다.
        # 이 함수는 item이라는 인자에 대해 적용되는데,
        # 이는 이 코드내에서 궁극적으로 각 행의 메세지를 가리키게 됩니다.

        Dls_for_item = Dls[Dls["tag"].isin(item.split())]  # item(메세지)을 split()을 통해 공백기준으로 전부 split 시킨 리스트로 리턴해줍니다.
        # 해당 메세지가 "서강대학교 경영학과 학부 건물은 바오로관과 마태오관이 있습니다"라고 하면,
        # item.split()의 리턴값은
        # ["서강대학교", "경영학과", "학부", "건물은", "바오로관과", "마태오관이", "있습니다"]입니다.
        # 리턴 값의 요소들이 나타난 부분만 찾아(.isin)    Dls_for_item이라는 변수에 저장합니다.

        for unit in list(Dls_for_item["tag"]):  # Dls_for_item데이터프레임에서 "tag"컬럼의 데이터를 리스트 형식으로 바꾼 후,
            # 이 리스트의 원소(unit)를 차례로 처리합니다. (for 반복문)
            item = item.replace(unit, tuple(Dls_for_item.loc[Dls_for_item["tag"] == unit, "Replace_Texts"])[0])
            # item(각 행의 메세지)은 unit차례로,
            # Dls_for_item에서 "Replace_Texts"에 해당히는 chink로 바꾼 것으로 치환한다.
            # Dls_for_item은 item의 원소 중 Dls에 있는 데이터만을 뽑아왔기 때문에
            # item에는 있으나 Dls에 없는 것을 탐색하는 불필요한 연산을 제거했다.

        return item  # item을 리턴한다.

    input_name = os.path.join(input_directory, input_)
    input_Message = import_dataframe(input_name)
    input_Message["contents"] = input_Message["contents"].progress_apply(lemmatize)  # .apply메소드를 통해
    # input_Message의 "contents" 컬럼에 행별로 lemmatize함수를 적용시킨다.
    input_Message = input_Message[input_Message["contents"].notna()]  # input_Message에 결측치들을 제거하고
    output_name = os.path.join(input_directory, output_)
    export_dataframe(input_Message, output_name)
    return input_Message  # 이 함수릐 리턴값으로 lemmatize된 input_Message를 준다.

########################################################################################################################

def Frequency_Analysis(text_file=None):
    import pandas as pd
    from collections import Counter
    from tqdm import tqdm as bar
    from .utils import Read_Arg_, import_dataframe, export_dataframe

    if text_file is None:
        for_cooc = 0  # 순수하게 Frequency_Analysis를 해야할 우
        ref, input_, output_ = Read_Arg_("Frequency_Analysis")
        Frequency_Gap = int(ref) / 100
        text = import_dataframe(input_)
    else:
        for_cooc = 1
        ref, _, _ = Read_Arg_("Frequency_Analysis", isind=1)
        Frequency_Gap = int(ref) / 100
        text = import_dataframe(text_file)

    def get_contents(item):
        if item != "":
            # not_language = re.compile('[^ ㄱ-ㅎㅣ가-힣|a-z|A-Z]+')
            # item = re.sub(not_language,"",str(item))
            item = item.lower()
            contents.append(item.strip())

    contents = []
    tag_contents = []
    text.contents.apply(get_contents)

    for token in contents:  # 요 파트를 스페이스 기준이 아닌걸로 수정해야 한다.
        for word in str(token).split(" "):
            if len(str(word)) > 1:
                tag_contents.append(word)
    counted_contents = Counter(tag_contents)

    tag_count = []

    for n, c in counted_contents.most_common():
        dics = {"tag": n, "count": c}
        tag_count.append(dics)

    df_tag_count = pd.DataFrame(tag_count)
    df_tag_count = df_tag_count[df_tag_count["count"] >= 500].sort_values(by="tag").reset_index(drop=True)
    iterations = len(df_tag_count)
    row_num = 0

    total = bar(range(iterations - 1), desc="comparing...")
    for t in total:
        step = t + 1
        std_row = df_tag_count.iloc[row_num]
        comparison_row = df_tag_count.shift(-1).iloc[row_num]
        std_tag = str(std_row["tag"])
        std_count = std_row["count"]
        comparison_tag = str(comparison_row["tag"])
        comparison_count = comparison_row["count"]

        if std_tag == comparison_tag[:len(std_tag)]:
            frequency_gap = abs(std_count - comparison_count)
            if frequency_gap / std_count < Frequency_Gap:
                df_tag_count.iloc[row_num + 1, 1] = comparison_count + std_count
                df_tag_count = df_tag_count[df_tag_count["tag"] != std_tag].reset_index(drop=True)
            else:
                row_num = row_num + 1
                continue
        else:
            row_num = row_num + 1
            continue
        if step == iterations - 1:
            break

    df_tag_count = df_tag_count.sort_values(by="count", ascending=False).reset_index(drop=True)

    if for_cooc == 0:
        export_dataframe(df_tag_count, output_)
    else:
        pass

    return df_tag_count

########################################################################################################################

def make_cotable(freq_tag, mes_tbl):
    import pandas as pd
    from tqdm import tqdm
    import re

    Cooc_Table = pd.DataFrame(columns=freq_tag)
    for tag in tqdm(freq_tag, desc="calculating co-occurrence"):
        tag_count = []
        Message_including_tag = list(filter(lambda x: tag in str(x), list(mes_tbl.contents)))

        for item in freq_tag:
            tag_finder = re.compile(str(item))
            tag_count += [len(list(filter(lambda x: len(tag_finder.findall(str(x))) > 0, Message_including_tag)))]
        Cooc_Table.loc[len(Cooc_Table)] = tag_count

    CoTable = Cooc_Table[Cooc_Table.columns]

    for i in range(len(Cooc_Table)):
        CoTable.loc[i] = [0] * (i + 1) + list(CoTable.loc[i])[i + 1:]
    CoTable.index = Cooc_Table.columns
    return CoTable

########################################################################################################################

def cooc_table(text_file=None):
    from .utils import Read_Arg_, import_dataframe, export_dataframe
    from tqdm import tqdm

    if text_file is None:
        ind = 1 # 독립적으로 쓰이는 경우, Backbone사용
        ref, input_, output_ = Read_Arg_("cooc_table")
        Message_Df = import_dataframe(input_)
    else:
        ind = 0 # 다른 함수 내에서 사용될 경우
        Message_Df = import_dataframe(text_file)
    Freq_df = Frequency_Analysis(text_file=Message_Df)  # 검색어 포함 할 때
    Freq_100 = Freq_df[Freq_df["count"] >= Freq_df["count"].max() * 0.01]
    Freq_100_tag = list(Freq_100.tag)

    CoTable = make_cotable(Freq_100_tag, Message_Df)

    CoTable_stacked = CoTable.stack().reset_index()
    CoTable_stacked.rename(columns={'level_0': 'tag_1', 'level_1': 'tag_2', 0: 'cooccurrence_count'}, inplace=True)
    CoTable_stacked = CoTable_stacked[CoTable_stacked["cooccurrence_count"] > 0]

    # 강조표현, 지시대명사, 접속사 등의 크게 의미를 부여하지 못하는 불용어 설정
    # stopwords = ['좋다', '우리', '있다', '다른', '많다', "너무", "정말",
    #              "많이", "가장", "하지만", "아주", "그냥", "조금", "매우", "합니다",
    #              "그러나", "것이", "위해", "때문에", "그것은", "하고", "하다", "하는",
    #              "하지", "입니다", "에서", "것을", "동안", "이것은", "수있는", "같다",
    #              "곳은", "곳을", "여기에", "또는", "또한", "다시", "있으며", "모두",
    #              "특히", "것입니다", " 대한", "바로", "다음", "대해", "가지고", "있지만",
    #              "정말로", "따라", "여러", "그것을", "것은", "해서", "가다", "갔다", "싶다",
    #              "완전", "정말", "했는데", "역시", "근데", "했다", "진짜", "하세", "엄청",
    #              "아니", "는데", "아마", "왔어", "있습니다", "있는"]

    # def erase_stopwords(dataframe):
    #     for word in stopwords:
    #         DataFrame = dataframe[dataframe["tag_1"] != word]
    #         DataFrame = DataFrame[DataFrame["tag_2"] != word]
    #     return DataFrame
    #
    # CoTable_stacked = erase_stopwords(CoTable_stacked)
    CoTable_stacked["includes"] = CoTable_stacked.apply(
        lambda df: 1 if df["tag_1"] in df["tag_2"] else 1 if df["tag_2"] in df["tag_1"] else 0, axis=1)
    CoTable_stacked = CoTable_stacked[CoTable_stacked["includes"] != 1]
    CoTable_stacked = CoTable_stacked[CoTable_stacked.columns[:-1]]
    CoTable_stacked = CoTable_stacked.loc[
        CoTable_stacked["cooccurrence_count"] >= CoTable_stacked["cooccurrence_count"].max() * 0.05]
    CoTable_stacked = CoTable_stacked.sort_values(by='cooccurrence_count', ascending=False).reset_index(drop=True)

    keyword_dict = dict()
    for kw in tqdm(set(CoTable_stacked["tag_1"]) | set(CoTable_stacked["tag_2"])):
        keyword_dict[kw] = {
            "appearance": len(Message_Df[Message_Df["contents"].str.contains(kw)])
        }

    CoTable_stacked["W_1^n"] = CoTable_stacked["tag_1"].apply(
        lambda row: Freq_100.loc[Freq_100["tag"] == row, "count"].values[0])
    CoTable_stacked["W_2^n"] = CoTable_stacked["tag_2"].apply(
        lambda row: Freq_100.loc[Freq_100["tag"] == row, "count"].values[0])
    CoTable_stacked["W_1^m"] = CoTable_stacked["tag_1"].apply(lambda row: keyword_dict[row]["appearance"])
    CoTable_stacked["W_2^m"] = CoTable_stacked["tag_2"].apply(lambda row: keyword_dict[row]["appearance"])
    CoTable_stacked["W_(1|2)^m"] = CoTable_stacked["cooccurrence_count"]
    CoTable_stacked["W_(2|1)^m"] = CoTable_stacked["cooccurrence_count"]
    CoTable_stacked["W_(1and2)^m"] = CoTable_stacked["cooccurrence_count"]
    CoTable_stacked["W_(1or2)^m"] = CoTable_stacked["W_1^m"]+CoTable_stacked["W_2^m"]-CoTable_stacked["cooccurrence_count"]
    CoTable_stacked["W_1^n%"] = CoTable_stacked["W_1^n"] / Freq_100["count"].max()
    CoTable_stacked["W_2^n%"] = CoTable_stacked["W_2^n"] / Freq_100["count"].max()
    CoTable_stacked["W_1^m%"] = CoTable_stacked["W_1^m"] / len(Message_Df)
    CoTable_stacked["W_2^m%"] = CoTable_stacked["W_2^m"] / len(Message_Df)
    CoTable_stacked["W_(1|2)^m%"] = CoTable_stacked["cooccurrence_count"] / CoTable_stacked["W_2^m%"]
    CoTable_stacked["W_(2|1)^m%"] = CoTable_stacked["cooccurrence_count"] / CoTable_stacked["W_1^m%"]
    CoTable_stacked["W_(1and2)^m%"] = CoTable_stacked["W_(1and2)^m"] / len(Message_Df)
    CoTable_stacked["W_(1or2)^m%"] =  CoTable_stacked["W_(1or2)^m"] / len(Message_Df)
    CoTable_stacked["Fit(1|2)"] = CoTable_stacked["W_(1|2)^m%"] / CoTable_stacked["W_(2|1)^m%"]
    CoTable_stacked["pair"] = CoTable_stacked[["tag_1", "tag_2"]].apply(lambda row: "-".join(row), axis=1)

    if ind == 1:
        export_dataframe(CoTable_stacked, output_)
    else:
        pass
    #output_name = os.path.join(input_directory, output_)

    return CoTable_stacked

########################################################################################################################

__all__ = {'Delete_Messages',
           'Delete_Overlapped_Messages',
           'Delete_Characters',
           'Delete_Characters_by_Dic',
           'Delete_StandardStopwords',
           'Replace_Texts_in_Messages',
           'Replace_Texts_by_Dic',
           'Frequency_Analysis',
           'make_cotable',
           'cooc_table'
           }