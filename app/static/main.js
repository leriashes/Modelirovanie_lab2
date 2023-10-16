//Получение значений из ячеек таблицы
function get_values()
{
    values = [];
    let cells = document.querySelectorAll('.form-control')

    for(let i = 0; i < cells.length; i++)
    {
        values.push({val : cells[i].value});
    }

    return values;
}

//Проверка введённых значений и выделение неудовлетворительных
function bad_values(bad)
{
    result = (bad != null && bad.length != 0);
    let cells = document.querySelectorAll('.form-control');

    if (result)
    {
        bad_val = bad.split(' ');

        j = 0;
        for (i = 0; i < cells.length; i++)
        {
            k = parseInt(bad_val[j]);

            if (k == i)
            {
                cells[i].style.backgroundColor = "#ea9999";
                j++;
            }
            else
            {
                cells[i].style.backgroundColor = "#ffffff";
            }
            
        }
    }
    else
    {
        for (i = 0; i < cells.length; i++)
        {
            cells[i].style.backgroundColor = "#ffffff";
        }
    }
    
    return result;
}

//Прорисовка графика
function draw_graph(s, values, dt, Tres, table_number)
{
    var data = [];
    var colors = ['rgba(206, 42, 91, 0.6)', 'rgba(239, 141, 131, 0.6)', 'rgba(237, 178, 81, 0.6)', 'rgba(187, 247, 116, 0.6)', 'rgba(103, 224, 224, 0.6)', 'rgba(152, 101, 247, 0.6)', 'rgba(66, 41, 131, 0.6)', 'rgba(23, 53, 110, 0.3)'];

    len = values.length;

    for (i = 0; i < len; i += 7)
    {
        xz = []
        yz = ['Станок 7  ', 'Станок 6  ', 'Станок 5  ', 'Станок 4  ', 'Станок 3  ', 'Станок 2  ', 'Станок 1  '];

        for (j = 0; j < 7; j++)
        {
            xz.push(values[i + 6 - j])
        }

        for (j = 1; j < 7; j++)
        {
            data.push({
                x: [parseInt(dt[i + 7 - j])],
                y: [yz[j - 1]],
                name: 'Простой',
                orientation: 'h',
                width: 0.5,
                marker: {
                    color: colors[7],
                    width: 1
                },
                type: 'bar',
                showlegend: false,
            });
        }

        name_str = (i / 7 + 1).toString();

        if (table_number >= 2)
        {
            name_str += '(' + s[i / 7].toString() + ')';
        }

        data.push({
            x: xz,
            y: yz,
            name: name_str,
            orientation: 'h',
            width: 0.5,
            marker: {
                color: colors[s[i / 7] - 1],
                width: 1
            },
            type: 'bar'
        });

    }

    
    data.push({
        x: [0],
        y: ['B'],
        name: 'Простои станков',
        orientation: 'h',
        width: 0.5,
        marker: {
          color: 'rgba(23, 53, 110, 0.8)',
          width: 1
        },
        type: 'bar',
        visible: 'legendonly'
    }); 

       

    t = parseInt(Tres / 45) + 1
    

    var layout = {
    title: 'График Ганта',
    barmode: 'stack',
    legend:
    {
        traceorder: 'normal'
    },
    xaxis: {
        dtick: t,
        showline: true
    },
    annotations: [
        {
          x: Tres,
          y: 0,
          xref: 'x',
          yref: 'y',
          text: 'T = ' + Tres,
          showarrow: true,
          arrowhead: 3,
          ax: 20,
          ay: -40
        },
      ]
    };
    
    Plotly.newPlot("chart" + table_number.toString(), data, layout);

}

function findSeq()
{
    table_values = get_values();

    $.ajax({
        url: '',
        type: 'get',
        contentType: 'application/json',
        data: {
            action: 'countPS',
            cells_values: JSON.stringify(table_values),
        },

        success: function(response){

            if (!bad_values(response.bad))
            {
                P1 = response.P1s.split(' ');
                P2 = response.P2s.split(' ');
                Lambda = response.lambdas.split(' ');
                Seq = response.seq_str.split(' ');

                let p1 = document.querySelectorAll('.P1');
                let p2 = document.querySelectorAll('.P2');
                let lambda = document.querySelectorAll('.lambda');
                let seq = document.querySelectorAll('.seq');

                for (i = 0; i < p1.length; i++)
                {
                    p1[i].innerHTML = P1[i];
                    p2[i].innerHTML = P2[i];
                    lambda[i].innerHTML = Lambda[i];
                }

                for (i = 0; i < seq.length; i++)
                {
                    seq[i].innerHTML = Seq[i];
                }
            }
        }
    });
}


$(document).ready(function(){

    findSeq();

    $('#findSeq').click(function(e)
    {
        findSeq();
    });

    $('#drawGraph').click(function(e)
    {
        e.preventDefault();

        table_values = get_values();

        let cells = document.querySelectorAll('.form-control')

        $.ajax({
            url: '',
            type: 'get',
            contentType: 'application/json',
            data: {
                action: 'draw',
                cells_values: JSON.stringify(table_values),
            },

            success: function(response){

                if (!bad_values(response.bad))
                {
                    values = [];
                    
                    for(i = 0; i < cells.length; i++)
                    {
                        values.push(cells[i].value);
                    }

                    draw_graph([1, 2, 3, 4, 5, 6, 7], values, response.dt_str.split(' '), response.T, 1);

                    let a = document.querySelector('#cardChart1');
                    a.style.display = 'block';
                }

            }
            
        })
    });

    //Поиск решения, график по оптимальному решению
    $('#findDecision').click(function(e)
    {
        findSeq();

        e.preventDefault();
        
        table_values = get_values();
        
        $.ajax({
            url: '',
            type: 'get',
            contentType: 'application/json',
            data: {
                action: 'find',
                cells_values: JSON.stringify(table_values)
            },
            success: function(response){
                
                if (!bad_values(response.bad))
                {
                    Seq = response.seq_str.split(' ');
                    let seq = document.querySelectorAll('.new_seq');
                    let num_opt = document.querySelector('#seq_num');
                    num_opt.innerHTML = "Оптимальная последовательность: " + (response.num_opt + 1);

                    for (i = 0, j = 0; i < seq.length; i++, j += 4)
                    {
                        seq[i].innerHTML = Seq[(i - i % 7) / 7 + j];

                        if (j == 24)
                        {
                            j = -4;
                        }
                    }

                    Val_t = response.t_str.split(' ');
                    Val_T = response.T_str.split(' ');
                    let val_tT = document.querySelectorAll('.tT');

                    for (i = 0; i < val_tT.length; i++)
                    {
                        if (Val_t[i] == "0")
                            val_tT[i].innerHTML = Val_t[i] + '/';
                        else
                            val_tT[i].innerHTML = Val_t[i] + '/' + Val_T[i];
                    }

                    Val_Tpr = response.Tpr_str.split(' ');
                    Val_Tozh = response.Tozh_str.split(' ');
                    let val_Ti = document.querySelectorAll('.Ti');
                    let val_Tj = document.querySelectorAll('.Tj');
                    let val_Tij = document.querySelectorAll('.Tij');

                    for (i = 0, j = 0, k = 0; k < 32; k++)
                    {
                        if (k % 8 == 7)
                        {
                            val_Tij[j].innerHTML = Val_Tpr[k] + '\\' + Val_Tozh[k];
                            j++;
                        }
                        else
                        {
                            val_Tj[i].innerHTML = Val_Tpr[k];
                            val_Ti[i].innerHTML = Val_Tozh[k];
                            i++;
                        }
                    }

                    s = response.seq_opt.split(' ')
                    sequence = []
                    for (i = 0; i < 7; i++)
                    {
                        sequence.push(parseInt(s[i]))
                    }


                    let cells = document.querySelectorAll('.form-control')
                    values = [];
                    
                    for(i = 0; i < 7; i++)
                    {
                        for (j = 0; j < 7; j++)
                        {
                            values.push(cells[(sequence[i] - 1) * 7 + j].value);
                        }
                    }

                    draw_graph(sequence, values, response.dt_opt.split(' '), response.T, 2);

                    /*if (response.cond == null || response.cond == true)
                    {
                        let cells = document.querySelectorAll('.res-cell1');
                        var res = response.res.split(' ');
                        let s = [];

                        let n = res.length / 5;
                        values = []

                        for(i = 0; i < cells.length; i++)
                        {
                            if (i % n == 0)
                            {
                                s.push(parseInt(res[i]));
                            }
                            else
                            {
                                values.push(res[i])
                            }

                            cells[i].innerHTML = res[i];
                        }


                        if (response.mas_y == null)
                        {
                            draw_graph(s, response.mas_x.split(' '), null, response.T, values, 2);
                        }
                        else
                        {
                            let b = document.querySelector('#Johnson');
                            b.style.display = 'block';

                            draw_graph(s, response.mas_x.split(' '), response.mas_y.split(' '), response.T, values, 2);

                            if (response.jtime != null)
                            {
                                let j = document.querySelector('#jtime');
                                let p = document.querySelector('#ptime');
                                p.style.display = 'block';

                                j.innerHTML = "Время выполнения\n" + response.jtime;
                                p.innerHTML = "Время выполнения\n" + response.ptime;
                            }
                        }
                    }
                    else
                    {
                        let b = document.querySelector('#Johnson');
                        b.style.display = 'none';

                        let p = document.querySelector('#ptime');
                        p.style.display = 'none';
                    }

                    if (response.cond != null)
                    {
                        let cells = document.querySelectorAll('.res-cell2');
                        var res = response.pres.split(' ');
                        let s = [];

                        let n = res.length / 5;
                        values = []

                        for(i = 0; i < cells.length; i++)
                        {
                            if (i % n == 0)
                            {
                                s.push(parseInt(res[i]));
                            }
                            else
                            {
                                values.push(res[i])
                            }

                            cells[i].innerHTML = res[i];
                        }

                        draw_graph(s, response.pmas_x.split(' '), response.pmas_y.split(' '), response.pT, values, 3);
                    }
*/
                    let a = document.querySelector('#cardChart2');
                    a.style.display = 'block';
                }
            }
        })
    });

   }
)