import PySimpleGUI as sg

data = [['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9']]

layout = [[sg.Table(values=data, headings=['Column 1', 'Column 2', 'Column 3'], num_rows=10,
          key='-TABLE-', enable_events=True, auto_size_columns_to_fit=True)],
          [sg.Button('Modify Selected Cell'), sg.Button('Exit')]]

window = sg.Window('Table Modification', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Modify Selected Cell':
        selected_rows = values['-TABLE-'][0]
        selected_cols = values['-TABLE-'][1]
        if selected_rows and selected_cols:
            row, col = selected_rows[0], selected_cols[0]
            data[row][col] = sg.popup_get_text('Enter new value', default_text=data[row][col])
            window['-TABLE-'].update(values=data)

window.close()
SelectedRowIndexes，GetSelectedRow，get，SelectedRows,auto_size_columns_to_fit