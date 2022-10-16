
$(document).ready(function(){
    $('.electrodes').on('click', async function(){
        
        var $row = $(this).parents("tr");
        var $dis = $('td:nth-child(11)',$row).text();
        console.log($dis);
        let val = {
            mr_no: $('td:nth-child(1)', $row).text(),
            disease: $('td:nth-child(11)',$row).text()
        }
        const sendReq = await axios.post(`/electrodes/${JSON.stringify(val)}`, {});
        
        console.log(sendReq);
        var sibRow = $row.next();
        console.log(sendReq.data.electrode);
        var data = `<td> Patient Electrodes:</td> <td> ${sendReq.data.electrode}</td><td>Procedure:</td><td>Voltage: </td><td>${sendReq.data['procedure_data'][0]}</td><td> Time Duration:</td><td> ${sendReq.data['procedure_data'][1]}</td><td> No. of sessions:</td><td> ${sendReq.data['procedure_data'][2]}</td>`;
        $row.next('.add').html(data);
            
        if (sibRow.hasClass('hide')) {
            sibRow.show();
            sibRow.removeClass('hide');
        } else {
            sibRow.hide();
            sibRow.addClass('hide');
        }
    });
});


