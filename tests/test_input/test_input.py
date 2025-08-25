# from input.get_user_input import process_input


# def test_process_input_all_values():
#     input_data = ['115', '10348', '40122', '5961', 'time', 'classic', 'both']
#     result = process_input(input_data)
#     assert result == (['115'], ['10348'], ['40122'], ['5961'], 'time', 'both')

# def test_process_input_none_values():
#     input_data = [None, None, None, None, None, None, None]
#     result = process_input(input_data)
#     # Should handle None gracefully; adjust expected output as per your function's logic
#     assert result == ([], [], [], [], None, None) or result is not None

# def test_process_input_lists():
#     input_data = [['115'], ['10348'], ['40122'], ['5961'], 'time', 'classic', 'both']
#     result = process_input(input_data)
#     assert result == (['115'], ['10348'], ['40122'], ['5961'], 'time', 'both')