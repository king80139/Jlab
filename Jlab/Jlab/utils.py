def Read_Arg_(arguement):  # Backbone Dictionary 스프레드 시트의 ProjectLibrary(recent)시트를 기반으로,
    # argument에 들어갈 명령어의 참조파일, input파일, output파일을 리턴하는 함수입니다.

    Lib = Read_Sheet_('ProjectLibrary(recent)')  # worksheet를 pandas DataFrame으로 변환해줍니다.

    target_row = Lib.loc[
        Lib["*함수명/ parameter이름"] == "*" + arguement, ["Reference File (Information)", "Input File/Information",
                                                      "Output file", "Action Status"]]
    # 원하는 함수가 쓰여있는 행을 찾고, 이 행에서 참조파일, input 파일, output 파일을 가져옵니다.
    target_row = target_row[target_row["Action Status"] > 0]  # Action Status 고려하는 부분
    if len(target_row) == 0:
        print("실행가능한 함수가 없습니다. Backbone Dictionary의 Action Status를 확인하십시오. 에러메세지가 발생합니다.")
        return None

    else:
        refFile_info, Input_info, Output = target_row[target_row.columns[0]].values[0], \
                                           target_row[target_row.columns[1]].values[0], \
                                           target_row[target_row.columns[2]].values[0]

        return [refFile_info, Input_info, Output]  # 참조파일, input 파일, output 파일을 차례로 리턴해줍니다.


class OS:
    def encoding(self):
        import platform
        if platform.system() == "Darwin" or platform.system() == "Linux":
            encoding = "cp949"
        elif platform.system() == "Windows":
            encoding = "utf-8"
        else:
            encoding = "cp949"
        return encoding


def Read_Sheet_(sheet_name):  # Backbone Dictionary 스프레드 시트를 기반으로,
    # sheet_name에 들어갈 시트를 리턴하는 함수입니다.
    import pandas as pd
    import os

    try:
        worksheet = pd.read_excel("JlabMiner library Backbone Dictionary.xlsx",  # Backbone Dictionary가 있는 경로를 써줘야 합니다.
                                  sheet_name=sheet_name).fillna("")  # 창민아 여기에 서버에 올린 Library 주소를 쓰면 될거야.
    except FileNotFoundError as e:
        if os.path.splitext(sheet_name) == ".csv":
            opsys = OS()
            encoding = opsys.encoding()
            worksheet = pd.read_csv(sheet_name, encoding=encoding).fillna("")
        elif os.path.splitext(sheet_name) == ".xlsx":
            worksheet = pd.read_excel(sheet_name).fillna("")
        else:
            raise e

    return worksheet


def import_dataframe(input_name):
    import pandas as pd

    opsys = OS()
    encoding = opsys.encoding()

    if ".csv" in input_name:
        dataframe = pd.read_csv(input_name, encoding=encoding)
        return dataframe
    elif ".xlsx" in input_name:
        dataframe = pd.read_excel(input_name)
        return dataframe
    elif ".pkl" in input_name:
        dataframe = pd.read_pickle(input_name)
        return dataframe
    else:
        return input_name


def export_dataframe(dataframe, output_name):
    import os
    name, ext = os.path.splitext(output_name)

    opsys = OS()
    encoding = opsys.encoding()

    def export_(df, out_name, enc):

        try:
            df.to_csv(out_name, encoding=enc, index=False)
        except UnicodeEncodeError:
            df.to_excel(out_name, index=False)
            print("csv파일로 내보내는데 오류가 있어 .xlsx파일로 내보냅니다.")

    if ".csv" in output_name:
        export_(dataframe, output_name, encoding)

    elif ".xlsx" in output_name:
        dataframe.to_excel(output_name, index=False)

    elif (name != "") & (ext == ""):
        output_name = "".join([name, ".csv"])
        export_(dataframe, output_name, encoding)

    elif output_name == "":
        output_name = input("결과물 이름이 정해지지 지지 않았습니다. 결과물의 이름을 기입해주십시오(확장자 제외) : ")
        output_name = "".join([output_name, ".csv"])
        export_(dataframe, output_name, encoding)
    else:
        # export_(dataframe, output_name, encoding)
        dataframe.to_pickle("".join([name, ".pkl"]))
        print("오류 발생, 일단 pickle파일로 export.")
        pass


__all__ = ['OS', 'Read_Arg_', 'Read_Sheet_', 'import_dataframe', 'export_dataframe']
