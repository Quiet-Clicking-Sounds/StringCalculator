const socket = io();

function update_instrument() {
    socket.emit('instrument_updater', get_basic_instrument_information(), table_to_Obj('string_table'));
};


function get_basic_instrument_information() {
    var base_dict = {};
    base_dict['lowest_key'] = document.getElementById("lowest_key").value
    base_dict['highest_key'] = document.getElementById("highest_key").value
    base_dict['pitch'] = document.getElementById("pitch").value
    return base_dict
};

function table_to_Obj(tableID) {
    // via https://gist.github.com/mattheo-gist/4151867
    var table = document.getElementById(tableID)
    var rows = table.rows;
    var propCells = rows[0].cells;
    var results = [];
    var obj, row, cells;
    var  iLen=propCells.length
    // Use the rows for data
    // Could use tbody rows here to exclude header & footer
    // but starting from 1 gives required result
    for (var j = 1, jLen = rows.length; j < jLen; j++) {
        cells = rows[j].cells;
        obj = [];

        for (var k = 0; k < iLen; k++) {
            obj.push(cells[k].textContent || cells[k].innerText || cells[k].childNodes[0].value);
        };
        results.push(obj);
    };
    return results;
}

function make_input_element(defaultValue = "", type = 'text', id_ = false) {
    var node = document.createElement("input");
    node.setAttribute('value', defaultValue);
    node.setAttribute('type', type);
    if (!id_) { node.setAttribute('id', id_) };

    return node
}

function update_string_table_row(rowRef, dataArray) {
    dataArray: Array
    // std_note, name, frequency, wire_material, length, diameter, wire_count, force
    rowRef.insertCell(0).appendChild(document.createTextNode(dataArray[0])); // std_note
    rowRef.insertCell(1).appendChild(document.createTextNode(dataArray[1])); // name
    rowRef.insertCell(2).appendChild(document.createTextNode(dataArray[2])); // frequency
    rowRef.insertCell(3).appendChild(make_input_element(dataArray[3], 'text', dataArray[1] + "-material")); // wire_material [std_note+-materail]
    rowRef.insertCell(4).appendChild(make_input_element(dataArray[4], 'text', dataArray[1] + "-length")); // length [std_note+-length]
    rowRef.insertCell(5).appendChild(make_input_element(dataArray[5], 'text', dataArray[1] + "-diameter")); // diameter [std_note+-diameter]
    rowRef.insertCell(6).appendChild(make_input_element(dataArray[6], 'text', dataArray[1] + "-count")); // count [std_note+-count]
    rowRef.insertCell(7).appendChild(document.createTextNode(dataArray[7])); // force
};

function string_table_row_updater(data) {
    tableRef: HTMLTableElement
    console.log(data)
    let tableRef = document.getElementById('string_table');
    let currentRow = 1;
    for (const [key, dataList] of Object.entries(data)) {
        currentRow += 1
        rowRef: HTMLTableRowElement
        dataList: Array
        if (document.getElementById(key)) {
            var rowRef = document.getElementById(key);
            rowRef.textContent = '';
        } else {
            var rowRef = tableRef.insertRow(-1);
            rowRef.setAttribute("id", key);
        };
        update_string_table_row(rowRef, dataList);
    };
};

socket.on("responce", string_table_row_updater);
socket.onAny((event, ...args) => { console.log(`got ${event}`); });