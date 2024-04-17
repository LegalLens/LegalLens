# 초기 db 설정파일입니다.

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import sessionmaker
from resource.db_env import user, password, host, db_name

# 데이터베이스 연결 설정
# db_url = "mysql+pymysql://root:1234@localhost:3306/legal_db"
db_url = f"mysql+pymysql://{user}:{password}@{host}:3306/{db_name}"
engine = create_engine(db_url)
metadata = MetaData()

# 테이블 정의
precedent_table = Table('precedent', metadata,
    Column('CaseSerialNumber', Integer, primary_key=True, comment='판례정보일련번호'),
    Column('CaseName', Text, comment='사건명'),
    Column('CaseNumber', Text, comment='사건번호'),
    Column('JudgmentDate', Integer, comment='선고일자'),
    Column('JudgmentType', Text, comment='선고'),
    Column('CourtName', Text, comment='법원명'),
    Column('CaseType', Text, comment='사건종류명'),
    Column('VerdictType', Text, comment='판결유형'),
    Column('Matter', Text, comment='판시사항'),
    Column('Summary', Text, comment='판결요지'),
    Column('ReferenceArticle', Text, comment='참조조문'),
    Column('ReferenceCase', Text, comment='참조판례'),
)

# 기존 테이블 삭제 후 새 테이블 생성
metadata.drop_all(engine)
metadata.create_all(engine)

# 데이터 로드
df = pd.read_csv("precedent.csv", index_col=0)
df = df.rename(columns={
    '판례정보일련번호': 'CaseSerialNumber',
    '사건명': 'CaseName',
    '사건번호': 'CaseNumber',
    '선고일자': 'JudgmentDate',
    '선고': 'JudgmentType',
    '법원명': 'CourtName',
    '사건종류명': 'CaseType',
    '판결유형': 'VerdictType',
    '판시사항': 'Matter',
    '판결요지': 'Summary',
    '참조조문': 'ReferenceArticle',
    '참조판례': 'ReferenceCase',
    '전문': 'FullText'
})
df = df.where(pd.notna(df), None)

# 데이터 삽입
Session = sessionmaker(bind=engine)
session = Session()
try:
    for index, row in df.iterrows():
        stmt = precedent_table.insert().values(**row.to_dict())
        session.execute(stmt)
    session.commit()
except Exception as e:
    print(e)
    session.rollback()
finally:
    session.close()
