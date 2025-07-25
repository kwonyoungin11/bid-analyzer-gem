import pandas as pd

def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    """
    엑셀 파일을 불러와 분석에 필요한 형태로 데이터를 정제하고 준비합니다.
    이 함수는 Gem이 파일을 받았을 때 가장 먼저 호출됩니다.
    """
    print("데이터를 불러오고 전처리를 시작합니다...")
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

    # 분석에 필요한 필수 컬럼들
    required_cols = ['기초금액', '낙찰가', '입찰자상호']
    
    # 컬럼 존재 여부 확인
    if not all(col in df.columns for col in required_cols):
        print(f"오류: 필수 컬럼 {required_cols} 중 일부가 파일에 없습니다.")
        return None

    # 데이터 타입 변환 및 오류 처리
    df['기초금액'] = pd.to_numeric(df['기초금액'], errors='coerce')
    df['낙찰가'] = pd.to_numeric(df['낙찰가'], errors='coerce')
    
    # 필수 데이터가 없는 행 제거
    df.dropna(subset=required_cols, inplace=True)

    # 분석에 가장 중요한 '낙찰률' 파생 변수 생성
    # 0으로 나누는 오류를 방지하기 위해 기초금액이 0이 아닌 경우에만 계산
    df = df[df['기초금액'] > 0].copy()
    df['낙찰률'] = df['낙찰가'] / df['기초금액']

    print("데이터 준비가 완료되었습니다.")
    return df
