# import pytest
# import pandas as pd
# from unittest.mock import patch
# import utils.dataframe_utils as df_utils

# def setup_module(module):
#     # Reset global lists before each test module
#     df_utils.course_id_df.clear()
#     df_utils.quiz_id_df.clear()
#     df_utils.user_id_df.clear()
#     df_utils.accom_type_df.clear()
#     df_utils.accom_date_df.clear()
#     df_utils.quiz_type_df.clear()

# def test_compile_df_values_adds_data():
#     df_utils.compile_df_values('C1', 'Q1', 'U1', 'time', 'past', 'classic')
#     assert df_utils.course_id_df == ['C1']
#     assert df_utils.quiz_id_df == ['Q1']
#     assert df_utils.user_id_df == ['U1']
#     assert df_utils.accom_type_df == ['time']
#     assert df_utils.accom_date_df == ['past']
#     assert df_utils.quiz_type_df == ['classic']

# def test_create_df_returns_dataframe():
#     # Add some data
#     df_utils.compile_df_values('C2', 'Q2', 'U2', 'attempts', 'past', 'new')
#     df = df_utils.create_df()
#     assert isinstance(df, pd.DataFrame)
#     assert set(df.columns) == {'Course ID', 'Quiz ID', 'User IDs', 'Accommodation', 'Quiz Date', 'Quiz Type'}
#     assert 'C2' in df['Course ID'].values
#     assert 'Q2' in df['Quiz ID'].values
#     assert 'U2' in df['User IDs'].values
#     assert 'attempts' in df['Accommodation'].values
#     assert 'past' in df['Quiz Date'].values
#     assert 'new' in df['Quiz Type'].values

# def test_build_df_calls_is_accommodated_and_compiles(monkeypatch):
#     # Patch is_accommodated to return (True, '2024-01-01') always
#     monkeypatch.setattr(df_utils, 'is_accommodated', lambda *a, **k: (True, 'past'))
#     df_utils.course_id_df.clear()
#     df_utils.quiz_id_df.clear()
#     df_utils.user_id_df.clear()
#     df_utils.accom_type_df.clear()
#     df_utils.accom_date_df.clear()
#     df_utils.quiz_type_df.clear()
#     df_utils.build_df(['C3'], ['Q3'], ['U3'], 'time', 'past')
#     assert df_utils.course_id_df[-1] == 'C3'
#     assert df_utils.quiz_id_df[-1] == 'Q3'
#     assert df_utils.user_id_df[-1] == 'U3'
#     assert df_utils.accom_type_df[-1] == 'time'
#     assert df_utils.accom_date_df[-1] == 'past'
#     assert df_utils.quiz_type_df[-1] == 'classic' or df_utils.quiz_type_df[-1] == 'new'
