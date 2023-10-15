from app import app
from time import time
from flask import render_template, url_for , request, jsonify
import pandas as pd
import json
import plotly
import plotly.express as px
from datetime import datetime


def toStrArray(cells):

    cells_values = cells.split( '"},{"val":"')
    cells_values[0] = cells_values[0][9:len(cells_values[0])]
    cells_values[len(cells_values) - 1] = cells_values[len(cells_values) - 1][0:len(cells_values[len(cells_values) - 1]) - 3]

    return cells_values

def findBad(cells_values):
    bad_values = []
    i = 0

    #поиск ячеек с неудовлетворяющими значениями
    while i < len(cells_values):
        count = 0

        for j in range(len(cells_values[i])):
            if cells_values[i][j] >= '0' and cells_values[i][j] <= '9':
                count += 1
            else:
                break

        if count < len(cells_values[i]) or len(cells_values[i]) == 0:
            bad_values.append(str(i))
            
        i += 1

    return bad_values


def countTStart(n, step, start_values):
    sum_a = 0
    sum_b = 0
    sum_c = 0
    sum_x = 0
    sum_y = 0
    T = 0
    three = False

    mas_x = []
    mas_y = []

    xs = []
    ys = []

    if (step > 3):
        step = 1

    if (step == 3 or step == 5):
        three = True
        

    for i in range(0, n, step):
        sum_a += start_values[i // step][1]
        xs.append(max(sum_a - sum_x - sum_b, 0))
        sum_x += xs[i // step]
        sum_b += start_values[i // step][2]
        if (three):
            ys.append(max(sum_x + sum_b - sum_y - sum_c, 0))
            sum_y += ys[i // step]
            sum_c += start_values[i // step][3]

    for i in range(len(xs)):
        mas_x.append(str(xs[i]))
        if (three):
            mas_y.append(str(ys[i]))

        
    if (three):
        T = sum_y + sum_c
    else:
        T = sum_x + sum_b

    return (T, mas_x, mas_y)


def countT(n, values, type):
    return (countTStart(n, type + 2, values))

def countTseq(values, seq):
    sum_a = 0
    sum_b = 0
    sum_c = 0
    sum_x = 0
    sum_y = 0

    mas_x = []
    mas_y = []

    xs = []
    ys = []
    for i in range(len(seq)):
        sum_a += values[seq[i]][1]
        xs.append(max(sum_a - sum_x - sum_b, 0))
        sum_x += xs[i]
        sum_b += values[seq[i]][2]
        ys.append(max(sum_x + sum_b - sum_y - sum_c, 0))
        sum_y += ys[i]
        sum_c += values[seq[i]][3]

    for i in range(len(xs)):
        mas_x.append(str(xs[i]))
        mas_y.append(str(ys[i]))

    T = sum_y + sum_c

    return (T, mas_x, mas_y)


def JohnsonAlgorithm(start_values):
    mas_a = []
    mas_b = []

    k = len(start_values)
    for i in range(k):
        m = start_values[0][1]
        row = 0
        ind = 0
        for j in range(len(start_values)):
            for t in range(2):
                if (start_values[j][t + 1] < m):
                    m = start_values[j][t + 1]
                    row = j
                    ind = t
        
        if (ind == 0):
            mas_a.append(start_values[row])
        else:
            mas_b.append(start_values[row])

        start_values.pop(row)

    mas_b.reverse()
    result_values = mas_a + mas_b

    return result_values

def SortAsc(params, seq, param_number):

    seq = seq.copy()

    n = len(seq)

    for i in range(n - 1):
        for j in range(n - i - 1):
            if params[seq[j]][param_number] > params[seq[j + 1]][param_number]:
                seq[j], seq[j + 1] = seq[j + 1], seq[j]
    
    return seq

def SortDesc(params, seq, param_number):

    seq = seq.copy()

    n = len(seq)

    for i in range(n - 1):
        for j in range(n - i - 1):
            if params[seq[j]][param_number] < params[seq[j + 1]][param_number]:
                seq[j], seq[j + 1] = seq[j + 1], seq[j]
    
    return seq

def Rule1(params, D10, D2):

    #сортировка D10 в порядке возрастания P1
    seq = SortAsc(params, D10, 1)

    #сортировка D2 в порядке убывания P2
    seq += SortDesc(params, D2, 2)

    return seq


def Rule2(params):

    D = params.copy()

    n = len(D)

    #сортировка D в порядке убывания лямбда
    for i in range(n - 1):
        for j in range(n - i - 1):
            if D[j][3] < D[j + 1][3]:
                D[j], D[j + 1] = D[j + 1], D[j]

    seq = []

    for i in range(n):
        seq.append(D[i][0])
        
    return seq

def Rule3(params, D1, D0, D2):

    #сортировка D1 в порядке возрастания P1
    seq = SortAsc(params, D1, 1)

    #сортировка D0 в порядке возрастания P1
    seq += SortAsc(params, D0, 1)

    #сортировка D2 в порядке убывания P2
    seq += SortDesc(params, D2, 2)

    return seq

def Pairs(params, d):
    seq = []

    n = len(d) // 2

    for i in range(n):
        m = params[d[0]][2]
        k = 0

        for j in range(len(d)):
            if params[d[j]][2] > m:
                m = params[d[j]][2]
                k = j
        
        seq.append(d[k])
        d.pop(k)

        m = params[d[0]][1]
        k = 0

        for j in range(len(d)):
            if params[d[j]][1] < m:
                m = params[d[j]][1]
                k = j

        seq.append(d[k])
        d.pop(k)

    return seq

def Dx(params, seq, dx):

    n = len(seq)
    lx = params[dx][3]

    placed = False

    for i in range(0, n - 2, 2):
        m1 = max(params[seq[i]][3], params[seq[i + 1]][3])
        m2 = min(params[seq[i + 2]][3], params[seq[i + 3]][3])

        if (m1 >= lx >= m2):
            placed = True
            seq.insert(i + 2, dx)
            break

    if not placed and lx >= min(params[seq[0]][3], params[seq[1]][3]):
        placed = True
        seq.insert(0, dx)

    if not placed and lx <= max(params[seq[n - 2]][3], params[seq[n - 1]][3]):
        placed = True
        seq.append(dx)
        
    return seq

def Rule4(params, D1, D0, D2):
    d1 = D1.copy()
    d0 = D0.copy()
    d2 = D2.copy()

    seq = Pairs(params, d1)

    if (len(d1) != 0):
        if (len(d0) == 0 and len(d2) == 0):
            Dx(params, seq, d1[0])
        else:
            seq.append(d1[0])

            if (len(d0) != 0):
                dn = d0
            else:
                dn = d2
            
            m = params[dn[0]][1]
            k = 0

            for j in range(len(dn)):
                if params[dn[j]][1] < m:
                    m = params[dn[j]][1]
                    k = j

            seq.append(dn[k])
            dn.pop(k)

    
    seq += Pairs(params, d0)

    if (len(d0) != 0):
        if (len(d2) == 0):
            Dx(params, seq, d0[0])
        else:
            seq.append(d0[0])

            m = params[d2[0]][1]
            k = 0

            for j in range(len(d2)):
                if params[d2[j]][1] < m:
                    m = params[d2[j]][1]
                    k = j

            seq.append(d2[k])
            d2.pop(k)

    seq += Pairs(params, d2)

    if (len(d2) != 0):
        Dx(params, seq, d2[0])

    return seq


@app.route('/')
@app.route('/index')
def index():
    if request.is_json:
        cells_values = toStrArray(request.args.get('cells_values'))
        bad_values = findBad(cells_values)

        mas_x = []
        start_values = []

        if (len(bad_values) == 0):
            for i in range(0, len(cells_values), 7):
                v = [i]
                for j in range(7):
                    v.append(int(cells_values[i + j]))

                start_values.append(v)

            if (request.args.get('action') == 'countPS'):

                P1 = []
                P2 = []
                lamb = []

                params = []

                for i in range(7):
                    sum1 = 0
                    sum2 = 0

                    for j in range(4):
                        sum1 += start_values[i][j + 1]
                        sum2 += start_values[i][j + 4]

                    P1.append(str(sum1))
                    P2.append(str(sum2))
                    lamb.append(str(sum2 - sum1))

                    params.append([i, sum1, sum2, sum2 - sum1])

                D1 = []
                D0 = []
                D10 = []
                D2 = []

                for i in range(7):
                    if params[i][3] >= 0:
                        if params[i][3] > 0:
                            D1.append(params[i][0])
                        else:
                            D0.append(params[i][0])
                        D10.append(params[i][0])
                    else:
                        D2.append(params[i][0])

                sequences = [Rule1(params, D10, D2), Rule2(params), Rule3(params, D1, D0, D2), Rule4(params, D1, D0, D2)]

                seq_str = []

                for i in range(7):
                    for j in range(4):
                        seq_str.append(str(sequences[j][i] + 1))

                return jsonify({'P1s': (' ').join(P1), 'P2s': (' ').join(P2), 'lambdas': (' ').join(lamb), 'seq_str': (' ').join(seq_str)})

                #T, mas_x, y = countTStart(len(cells_values), 2, start_values)

                #return jsonify({'T': T, 'mas_x': (' ').join(mas_x)})

            #Прорисовка графика по исходным значениям - вычисление x
            elif (request.args.get('action') == 'draw'):

                T, mas_x, y = countTStart(len(cells_values), 2, start_values)

                return jsonify({'T': T, 'mas_x': (' ').join(mas_x)})

            #Поиск решения
            elif (request.args.get('action') == 'find'):
                
                result_values = JohnsonAlgorithm(start_values)
                res_str = []

                for i in range(len(result_values)):
                    for j in range(3):
                        res_str.append(str(result_values[i][j] + 1 * (j == 0)))

                T, mas_x, y = countT(len(result_values), result_values, 2)

                return jsonify({'T': T, 'mas_x': (' ').join(mas_x), 'res': (' ').join(res_str)})
        return jsonify({'bad': (' ').join(bad_values)})
    else:
        return render_template("index.html", title = "Задача для 2 станков", type = 2)


    if request.is_json:
        cells_values = toStrArray(request.args.get('cells_values'))
        bad_values = findBad(cells_values)

        mas_x = []
        mas_y = []
        start_values = []

        if (len(bad_values) == 0):

            for i in range(0, len(cells_values), 3):
                start_values.append([i // 3, int(cells_values[i]), int(cells_values[i + 1]), int(cells_values[i + 2])])

            #Прорисовка графика по исходным значениям - вычисление x, y
            if (request.args.get('action') == 'draw'):
                T, mas_x, mas_y = countTStart(len(cells_values), 3, start_values)

                return jsonify({'bad': (' ').join(bad_values), 'T': T, 'mas_x': (' ').join(mas_x), 'mas_y': (' ').join(mas_y)})

            #Поиск решения
            elif (request.args.get('action') == 'find'):
                # метод перебора
                pT, pmas_x, pmas_y = countTStart(len(cells_values), 3, start_values)
                ps = [0, 1, 2, 3, 4]
                prs = [0, 1, 2, 3, 4]
                n = len(ps)
                j = 1

                start_time = datetime.now()

                while True:
                    i = 3
                    while i != -1 and ps[i] >= ps[i + 1]:
                        i -= 1
                    if i == -1:
                        break
                    
                    k = n - 1
                    while ps[i] >= ps[k]:
                        k -= 1

                    ps[i], ps[k] = ps[k], ps[i]

                    l = i + 1
                    r = n - 1

                    while l < r:
                        ps[l], ps[r] = ps[r], ps[l]
                        l += 1
                        r -= 1

                    tT, tmas_x, tmas_y = countTseq(start_values, ps)

                    print("yay", tT, pT, tT < pT)
                    if (tT < pT):
                        prs = ps.copy()
                        pT = tT
                        pmas_x = tmas_x
                        pmas_y = tmas_y
                        print("yay")
                    j += 1

                    print(j, prs, ps, tT, pT)

                ptime = datetime.now() - start_time
                print(ptime)

                print(prs, ps)
                pres_str = []

                for i in range(len(prs)):
                    pres_str.append(str(prs[i] + 1))
                    for j in range(3):
                        pres_str.append(str(start_values[prs[i]][j + 1]))

                #проверка условия Джонсона
                min_a = start_values[0][1]
                max_b = start_values[0][2]
                min_c = start_values[0][3]

                for i in range(1, len(start_values)):
                    if (start_values[i][1] < min_a):
                        min_a = start_values[i][1]
                    if (start_values[i][2] > max_b):
                        max_b = start_values[i][2]
                    if (start_values[i][3] < min_c):
                        min_c = start_values[i][3]

                cond = (min_a >= max_b) or (min_c >= max_b)

                if (cond):

                    start_time = datetime.now()

                    de_values = []

                    for i in range(len(start_values)):
                        de_values.append([start_values[i][0], start_values[i][1] + start_values[i][2], start_values[i][2] + start_values[i][3]])

                    result_values = JohnsonAlgorithm(de_values)

                    seq = []
                    for i in range(len(result_values)):
                        seq.append(result_values[i][0])

                    T, mas_x, mas_y = countTseq(start_values, seq)

                    jtime = datetime.now() - start_time

                    print(jtime)



                    res_str = []

                    for i in range(len(result_values)):
                        res_str.append(str(result_values[i][0] + 1))
                        for j in range(3):
                            res_str.append(str(start_values[result_values[i][0]][j + 1]))

                    return jsonify({'jtime': str(jtime), 'ptime': str(ptime), 'pT': pT, 'pmas_x': (' ').join(pmas_x), 'pmas_y': (' ').join(pmas_y), 'pres': (' ').join(pres_str), 'T': T, 'mas_x': (' ').join(mas_x), 'mas_y': (' ').join(mas_y), 'res': (' ').join(res_str), 'cond': cond})
                return jsonify({'pT': pT, 'pmas_x': (' ').join(pmas_x), 'pmas_y': (' ').join(pmas_y), 'pres': (' ').join(pres_str), 'cond': cond})
                
        return jsonify({'bad': (' ').join(bad_values)})
    else:
        return render_template("index.html", title = "Задача для 3 станков", type = 3)