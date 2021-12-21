const socket = io();

function update_instrument() {
    socket.emit('instrument_updater', get_basic_instrument_information());
};


function get_basic_instrument_information() {
    var base_dict = {};
    base_dict['lowest_key'] = document.getElementById("lowest_key").value
    base_dict['highest_key'] = document.getElementById("highest_key").value
    base_dict['pitch'] = document.getElementById("pitch").value
    return base_dict
};


function update_table_row(rowElement, dataList) {
    rowElement: HTMLTableRowElement
    dataList: Array

};

function string_table_row_updater(data) {
    tableRef: HTMLTableElement
    let tableRef = document.getElementById('string_table');
    let currentRow = 1;
    for (const [key, dataList] of Object.entries(data)) {
        currentRow += 1
        rowRef: HTMLTableRowElement
        dataList: Array
        if (document.getElementById(key)) {
            var rowRef = document.getElementById(key);
        } else {
            var rowRef = tableRef.insertRow(-1);
            rowRef.setAttribute("id", key);
        };
        dataList.forEach(element => {
            newCell: HTMLTableCellElement
            let newCell = rowRef.insertCell(-1);
            let newText = document.createTextNode(element);
            newCell.appendChild(newText);
        });
    };
};

socket.on("responce", string_table_row_updater);
socket.onAny((event, ...args) => { console.log(`got ${event}`); });