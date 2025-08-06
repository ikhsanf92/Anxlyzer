from flask import Blueprint, render_template, request
from .utils import predict_result, generate_indicators, hasil_kecemasan, generate_swl_chart, generate_spin_chart, generate_gaming_pie_chart, generate_indikator_chart, generate_radar_chart, generate_gad_score_from_label
from flask import Blueprint, render_template, request, redirect, url_for, session

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.to_dict()
        pred_label = predict_result(user_input)
        return render_template('result.html', prediction=pred_label)
    return render_template('home.html')

@main.route('/form/personal', methods=['GET', 'POST'])
def form_personal():
    if request.method == 'POST':
        session['Gender'] = request.form.get('Gender')
        session['Age'] = request.form.get('Age')
        session['Work'] = request.form.get('Work')
        session['Degree'] = request.form.get('Degree')
        return redirect(url_for('main.form_game_part1'))
    return render_template('form_personal.html')

@main.route('/form/game/part1', methods=['GET', 'POST'])
def form_game_part1():
    if request.method == 'POST':
        session['Genre'] = request.form.get('Genre')
        session['GameName'] = request.form.get('GameName')
        session['Playstyle'] = request.form.get('Playstyle')
        return redirect(url_for('main.form_game_part2'))
    return render_template('form_game_part1.html', current_part=1)

@main.route('/form/game/part2', methods=['GET', 'POST'])
def form_game_part2():
    if request.method == 'POST':
        weekdays = int(request.form.get('HoursWeekdays') or 0)
        weekend = int(request.form.get('HoursWeekend') or 0)
        
        session['HoursWeekdays'] = weekdays
        session['HoursWeekend'] = weekend
        session['Hours'] = weekdays + weekend
        return redirect(url_for('main.form_game_part3'))
    return render_template('form_game_part2.html', current_part=2)

@main.route('/form/game/part3', methods=['GET', 'POST'])
def form_game_part3():
    if request.method == 'POST':
        session['whyplay'] = request.form.get('whyplay')
        session['GADE'] = request.form.get('GADE')
        session['streams'] = request.form.get('streams')
        return redirect(url_for('main.form_game_part4'))
    return render_template('form_game_part3.html', current_part=3)

@main.route('/form/game/part4', methods=['GET', 'POST'])
def form_game_part4():
    if request.method == 'POST':
        session['Narcissism'] = request.form.get('Narcissism')
        return redirect(url_for('main.swl_info'))
    return render_template('form_game_part4.html', current_part=4)

@main.route('/swl/info')
def swl_info():
    return render_template('swl_info.html')

@main.route('/kuisioner/swl/<int:number>', methods=['GET', 'POST'])
def swl_question(number):
    if request.method == 'POST':
        value = request.form.get(f"SWL{number}")
        session[f"SWL{number}"] = value

        if number < 5:
            return redirect(url_for('main.swl_question', number=number + 1))
        else:
            return redirect(url_for('main.spin_info'))

    question_text, help_text = get_swl_question(number)
    return render_template('swl_question.html', number=number, question=question_text, help_text=help_text)

def get_swl_question(number):
    questions = {
        1: "Hidup saya sekarang terasa cukup dekat dengan apa yang saya inginkan.",
        2: "Kondisi hidup saya saat ini terasa cukup baik.",
        3: "Saya merasa sudah mendapatkan hal-hal penting yang saya inginkan dalam hidup.",
        4: "Kalau saya bisa mengulang hidup dari awal, saya tidak akan mengubah banyak hal.",
        5: "Secara keseluruhan, saya puas dengan hidup saya."
    }

    descriptions = {
        1: "Menilai apakah hidupmu sudah seperti yang kamu harapkan, misalnya bisa sekolah di tempat yang kamu mau, atau membeli sesuatu yang kamu suka.",
        2: "Menilai bagaimana kamu memandang kehidupanmu saat ini secara umum — seperti apakah kamu merasa cukup nyaman, aman, dan tidak terlalu banyak masalah besar.",
        3: "Maksudnya adalah apakah kamu merasa sudah memiliki atau mengalami hal-hal yang penting buat kamu, seperti teman dekat, pengalaman menyenangkan, atau pencapaian pribadi.",
        4: "Menilai apakah kamu cukup puas dengan kehidupanmu sejauh ini, sampai-sampai kamu tidak merasa perlu mengubah banyak hal kalau diberi kesempatan mengulang dari awal.",
        5: "Pernyataan ini mengukur sejauh mana kamu merasa puas dengan hidupmu secara keseluruhan, baik dari sisi sekolah, pertemanan, keluarga, dan hal penting lainnya dalam hidupmu."
    }
    return questions.get(number, "Pertanyaan tidak ditemukan."), descriptions.get(number, "")

@main.route('/spin/info')
def spin_info():
    return render_template('spin_info.html')

@main.route('/kuisioner/spin/<int:number>', methods=['GET', 'POST'])
def spin_question(number):
    if request.method == 'POST':
        value = request.form.get(f"SPIN{number}")
        session[f"SPIN{number}"] = value

        if number < 17:
            return redirect(url_for('main.spin_question', number=number + 1))
        else:
            user_input = dict(session)

            # Hitung SPIN_T dan SWL_T dulu
            spin_total = sum(int(user_input.get(f"SPIN{i}", 0)) for i in range(1, 18))
            swl_total = sum(int(user_input.get(f"SWL{i}", 0)) for i in range(1, 6))

            user_input["SPIN_T"] = spin_total
            user_input["SWL_T"] = swl_total

            # Simpan ke session jika ingin dipakai lagi
            session["SPIN_T"] = spin_total
            session["SWL_T"] = swl_total
            session['user_input'] = user_input 

            # Lanjut proses prediksi
            pred_label = predict_result(user_input)
            indicator = generate_indicators(pred_label, user_input)
            gad_total = sum([int(request.form.get(f"GAD{i+1}", 0)) for i in range(7)])
            session['GAD_Score'] = gad_total
            session['prediction'] = pred_label
            session['indicator'] = indicator


            return redirect(url_for('main.result'))

    question_text, help_text = get_spin_question(number)
    return render_template(
        'spin_question.html',
        number=number,
        question=question_text,
        help_text=help_text
    )

def get_spin_question(number):
    questions = {
        1: "Saya merasa gugup saat bertemu orang baru.",
        2: "Saya menghindari berbicara di depan umum.",
        3: "Saya merasa tidak nyaman saat diperhatikan oleh orang lain.",
        4: "Saya takut mempermalukan diri di depan orang lain.",
        5: "Saya menghindari kegiatan sosial.",
        6: "Saya takut orang lain akan menghakimi saya.",
        7: "Saya cemas saat harus bicara dengan orang penting.",
        8: "Saya merasa malu tanpa alasan yang jelas.",
        9: "Saya merasa sulit untuk mulai berbicara dengan orang lain.",
        10: "Saya khawatir orang lain tidak menyukai saya.",
        11: "Saya menghindari kontak mata dengan orang lain.",
        12: "Saya gugup saat harus memperkenalkan diri.",
        13: "Saya merasa cemas saat berada di tempat umum.",
        14: "Saya sulit menikmati acara sosial karena kecemasan.",
        15: "Saya takut melakukan kesalahan saat dilihat orang.",
        16: "Saya khawatir cara saya bicara terdengar aneh.",
        17: "Saya sangat gelisah sebelum acara sosial."
    }
        
    descriptions = {
        1: "Menilai apakah kamu sering merasa gugup atau tegang saat bertemu dengan orang yang belum dikenal.",
        2: "Apakah kamu sering menolak berbicara di depan banyak orang karena merasa takut atau cemas?",
        3: "Apakah kamu merasa gugup atau tidak tenang jika orang lain memperhatikanmu saat melakukan sesuatu?",
        4: "Apakah kamu merasa takut melakukan sesuatu yang bisa membuatmu terlihat bodoh di depan orang lain?",
        5: "Apakah kamu sering memilih untuk tidak ikut acara atau pertemuan karena merasa cemas?",
        6: "Apakah kamu merasa takut jika orang lain menilai atau berpikir negatif tentangmu?",
        7: "Apakah kamu merasa tegang atau gugup saat berbicara dengan guru, dosen, atau orang yang kamu anggap penting?",
        8: "Apakah kamu sering merasa malu di situasi sosial, meskipun tidak terjadi apa-apa yang salah?",
        9: "Apakah kamu merasa ragu atau canggung ketika harus memulai pembicaraan dengan orang lain?",
        10: "Apakah kamu sering memikirkan apakah orang lain suka atau tidak dengan dirimu?",
        11: "Apakah kamu merasa tidak nyaman menatap mata orang saat berbicara dengan mereka?",
        12: "Apakah kamu merasa cemas ketika harus memperkenalkan dirimu di depan orang lain?",
        13: "Apakah kamu merasa tidak nyaman saat berada di tempat ramai seperti mall atau acara besar?",
        14: "Apakah rasa cemas membuatmu tidak bisa menikmati waktu saat kumpul-kumpul atau acara sosial?",
        15: "Apakah kamu khawatir akan membuat kesalahan jika ada orang lain yang memperhatikanmu?",
        16: "Apakah kamu merasa tidak percaya diri dengan cara kamu berbicara di depan orang lain?",
        17: "Apakah kamu merasa sangat cemas atau tidak tenang sebelum harus hadir di acara bersama orang banyak?",
    }
    return questions.get(number, "Pertanyaan tidak ditemukan."), descriptions.get(number, "")

@main.route('/hasil', methods=['GET'])
def result():
    prediction = session.get('prediction')
    indicator = session.get('indicator')

    if prediction is None:
        return "Belum ada hasil prediksi. Silakan isi kuesioner terlebih dahulu.", 400

    deskripsi = hasil_kecemasan[prediction]['deskripsi']
    rekomendasi = hasil_kecemasan[prediction]['rekomendasi']
    
    user_input = dict(session)
    swl_scores = [int(session.get(f"SWL{i+1}", 0)) for i in range(5)]
    spin_scores = [int(session.get(f"SPIN{i+1}", 0)) for i in range(17)]
    jam_main = int(session.get('Hours') or 0)
    nonton_stream = int(session.get('streams') or 0)
    antusiasme = int(session.get('Narcissism') or 3)
    
    pie_chart = generate_gaming_pie_chart(jam_main, nonton_stream, antusiasme)
    swl_chart = generate_swl_chart(swl_scores)
    spin_chart = generate_spin_chart(spin_scores)
    indikator_chart = generate_indikator_chart(user_input)
    radar_chart = generate_radar_chart(session)
    
    spin_total = sum(spin_scores)
    swl_total = sum(swl_scores)
    
    gad_score_value = generate_gad_score_from_label(prediction)

    def interpret_gad(score):
        if score is None:
            return "Tidak tersedia"
        elif score <= 4:
            return "Hampir tidak ada gejala kecemasan"
        elif score <= 9:
            return "Ada gejala kecemasan ringan, tapi masih terkendali"
        elif score <= 14:
            return "Gejala kecemasan cukup terasa dan mulai memengaruhi keseharian"
        else:
            return "Gejala kecemasan cukup kuat, sebaiknya perhatikan lebih serius"
    gad_interpret = interpret_gad(gad_score_value)
    
    def interpret_spin(score):
        if score <= 20:
            return "Kecemasan sosial sangat rendah, kamu cukup nyaman berinteraksi."
        elif score <= 30:
            return "Ada sedikit kecemasan sosial, tapi masih wajar."
        elif score <= 45:
            return "Kamu cukup sering merasa cemas dalam situasi sosial."
        elif score <= 68:
            return "Kecemasan sosialmu cukup tinggi dan bisa memengaruhi aktivitasmu."
        else:
            return "Kamu menunjukkan tanda-tanda fobia sosial yang cukup kuat."
    
    def interpret_swl(score):
        if score <= 14:
            return "Kamu kurang puas dengan hidupmu saat ini."
        elif score <= 19:
            return "Kehidupanmu cukup baik, tapi masih banyak yang ingin dicapai."
        elif score <= 25:
            return "Kamu cukup puas dengan hidupmu secara umum."
        else:
            return "Kamu sangat puas dengan hidupmu."
    spin_interpret = interpret_spin(spin_total)
    swl_interpret = interpret_swl(swl_total)

    age = int(session.get('Age') or 0)
    needs_parental_guidance = 12 <= age <= 17
    
    show_support_section = prediction in ["Sedang", "Tinggi"]
    
    # Di render_template
    return render_template(
        'result.html',
        prediction=prediction,
        deskripsi=deskripsi,
        rekomendasi=rekomendasi,
        indicator=indicator,
        swl_chart=swl_chart,
        spin_chart=spin_chart,
        gaming_chart=pie_chart,
        indikator_chart=indikator_chart,
        radar_chart=radar_chart,
        gad_score_value=gad_score_value,
        gad_interpret=gad_interpret,
        data={
            "SPIN_T": spin_total,
            "SWL_T": swl_total,
        },
        spin_interpret=spin_interpret,
        swl_interpret=swl_interpret,
        needs_parental_guidance=needs_parental_guidance,
        show_support_section=show_support_section,
    )
