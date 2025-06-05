from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Global storage
simulations = []
current_matrix = None
current_contagions = set()

def generate_matrix(N, max_conn=4):
    matriz = [[0]*N for _ in range(N)]
    for i in range(N):
        posibles = list(range(N))
        random.shuffle(posibles)
        matriz[i][i] = 1
        conexiones = 0
        for j in posibles:
            if conexiones >= max_conn:
                break
            if matriz[i][j] == 0 and matriz[j][i] == 0:
                matriz[i][j] = 1
                conexiones += 1
    return matriz

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/option/<int:opt>', methods=['GET', 'POST'])
def option(opt):
    global current_matrix, current_contagions
    if opt == 1:
        if request.method == 'POST':
            N = int(request.form['N'])
            tasa = float(request.form['tasa'])
            Y = float(request.form['Y'])

            # Por defecto: aleatorio
            if request.form.get('manual_checkbox') == 'on':
                # El usuario decidió ingresar manualmente
                try:
                    emp0 = int(request.form['emp0'])
                except (ValueError, TypeError):
                    error = "Debes ingresar un número de empleado válido."
                    return render_template('option1.html', error=error)

                if emp0 < 1 or emp0 > N:
                    error = "Empleado inicial inválido (debe estar entre 1 y {}).".format(N)
                    return render_template('option1.html', error=error)
            else:
                # No marcó "manual", elijo aleatorio
                emp0 = random.randint(1, N)

            current_matrix = generate_matrix(N)
            objetivo = int((Y / 100) * N)
            contagiados = {emp0 - 1}
            dias_cont = {emp0 - 1: 0}
            dias = 0
            historial = [[emp0]]
            while len(contagiados) < objetivo:
                dias += 1
                new = set()
                for c in list(contagiados):
                    if dias - dias_cont[c] < 3:
                        for j, val in enumerate(current_matrix[c]):
                            if val and j not in contagiados:
                                if random.random() * 100 <= tasa:
                                    new.add(j)
                if not new:
                    break
                for n in new:
                    dias_cont[n] = dias
                contagiados |= new
                historial.append([x + 1 for x in new])

            simulations.append({
                'emp0': emp0,
                'dias': dias,
                'total': len(contagiados),
                'objetivo': objetivo,
                'hist': historial
            })
            current_contagions = set(contagiados)

            alcanzado = len(contagiados) >= objetivo

            return render_template(
                'result1.html',
                dias=dias,
                total=len(contagiados),
                N=N,
                objetivo=objetivo,
                alcanzado=alcanzado
            )
        # GET: mostrar formulario
        return render_template('option1.html')

    elif opt == 2:
        if current_matrix is None:
            return redirect(url_for('option', opt=1))
        return render_template('matrix.html', matrix=current_matrix)

    elif opt == 3:
        if request.method == 'POST':
            e1 = int(request.form['e1']) - 1
            e2 = int(request.form['e2']) - 1
            from collections import deque
            q = deque([(e1, [e1])])
            visited = {e1}
            path = []
            while q:
                cur, p = q.popleft()
                if cur == e2:
                    path = p
                    break
                for j, val in enumerate(current_matrix[cur]):
                    if val and j not in visited:
                        visited.add(j)
                        q.append((j, p + [j]))
            dist = len(path) - 1 if path else 0
            path_display = [x + 1 for x in path]
            return render_template('result3.html',
                                   path=path_display,
                                   dist=dist,
                                   e1=e1 + 1,
                                   e2=e2 + 1)
        return render_template('option3.html')

    elif opt == 4:
        if request.method == 'POST':
            t = int(request.form['t']) - 1
            status = t in current_contagions
            return render_template('result4.html',
                                   t=t + 1,
                                   status=status)
        return render_template('option4.html')

    elif opt == 5:
        return render_template('simulations.html', sims=simulations)

    elif opt == 6:
        creditos = [
            "Tremolada Villanueva, Jeronimo Alonso - U202413264",
            "Retamozo Meza, Javier Xande - U202423385",
            "Um Camahuali, Leonardo Fabricio - U202411355",
            "Vera Suarez, Rodrigo - U202422941",

        ]
        return render_template('credits.html', creditos=creditos)

    else:
        return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(debug=True)
