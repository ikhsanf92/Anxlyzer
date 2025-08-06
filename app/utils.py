import joblib
import random
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import os
import requests

def download_file_if_missing(url, local_path):
    if not os.path.exists(local_path):
        print(f"File {local_path} tidak ditemukan. Mengunduh dari {url}...")
        response = requests.get(url, stream=True)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"File {local_path} berhasil diunduh.")

# Ganti URL berikut dengan direct download link modelmu
MODEL_URL = "https://drive.google.com/uc?export=download&id=1XgdO-VzZZZ1z7jk6MdzlBRfjYuI3z_BD"

download_file_if_missing(MODEL_URL, 'app/models/model_rf_sm.pkl')

model = joblib.load('app/models/model_rf_sm.pkl')
scaler = joblib.load('app/models/scaler.pkl')
label_encoders = joblib.load('app/models/label_encoders.pkl')
le_y = joblib.load('app/models/label_encoder_y.pkl')

with open('app/models/feature_columns.txt') as f:
    feature_columns = [line.strip() for line in f]

def predict_result(user_input):
    df = pd.DataFrame([user_input])

    # Pastikan string lowercase dan strip
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.lower().str.strip()

    # Label Encoding
    for col in df.columns:
        if col in label_encoders:
            le = label_encoders[col]
            val = df[col].iloc[0]
            if val not in le.classes_:
                le.classes_ = np.append(le.classes_, val)
            df[col] = le.transform([val])

    # Konversi kolom SWL1–SWL5 ke int
    for i in range(1, 6):
        df[f'SWL{i}'] = pd.to_numeric(df[f'SWL{i}'])

    # Konversi kolom SPIN1–SPIN17 ke int
    for i in range(1, 18):
        df[f'SPIN{i}'] = pd.to_numeric(df[f'SPIN{i}'])
        
    # Konversi ke tipe numerik
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce').fillna(0)
    df['streams'] = pd.to_numeric(df['streams'])
    df['Narcissism'] = pd.to_numeric(df['Narcissism'])

    # Hitung kolom turunan
    df['SWL_T'] = df[[f'SWL{i}' for i in range(1,6)]].sum(axis=1)
    df['SPIN_T'] = df[[f'SPIN{i}' for i in range(1,18)]].sum(axis=1)
    df['gaming_intensity'] = df['Hours'] + df['streams']
    df['narc_play'] = df['Hours'] * df['Narcissism']

    # Pastikan urutan sesuai fitur model
    df = df[feature_columns]

    # Scaling
    df_scaled = pd.DataFrame(scaler.transform(df), columns=feature_columns)

    # Prediksi
    pred = model.predict(df_scaled)[0]
    label = le_y.inverse_transform([pred])[0]
    return label

hasil_kecemasan = {
    "Rendah": {
        "deskripsi": "Gejala cemas kamu tergolong ringan banget atau hampir nggak ada. Ini artinya kamu punya kontrol yang cukup baik terhadap pikiran dan perasaan kamu.",
        "rekomendasi": [
            "Jaga pola hidup sehat seperti tidur yang cukup, makan teratur, dan olahraga ringan bisa bantu kamu tetap stabil secara emosional.",
            "Tetap lanjutkan aktivitas positif yang bikin kamu senang, seperti main game secukupnya, nongkrong sama teman, atau ngulik hobi.",
            "Coba teknik tenangin diri, misalnya tarik napas dalam pelan-pelan waktu lagi stres atau sebelum tidur.",
            "Bikin rutinitas harian yang seimbang, biar kamu tetap fokus dan nggak gampang kecemasan kecil datang."
        ]
    },
    "Ringan": {
        "deskripsi": "Kamu mulai ngerasa agak cemas, tapi belum terlalu mengganggu aktivitas. Ini bisa muncul karena capek sekolah, overthinking, atau hal kecil yang numpuk.",
        "rekomendasi": [
            "Luangin waktu buat diri sendiri. Jalan-jalan sebentar, baca buku, dengerin lagu, atau ngelakuin hal yang kamu suka bisa bantu ngurangin rasa cemas.",
            "Main game boleh, tapi jangan dijadikan pelarian utama. Coba atur waktu main biar kamu nggak makin ngehindar dari masalah.",
            "Tulis apa yang kamu rasain. Kadang, nulis di notes atau jurnal bisa bikin pikiran lebih lega.",
            "Cari tempat cerita. Teman atau keluarga yang bisa dipercaya bisa bantu kamu lihat masalah dari sudut pandang yang berbeda."
        ]
    },
    "Sedang": {
        "deskripsi": "Rasa cemasmu udah cukup terasa dan mulai ganggu sekolah, kerja, atau hubungan sosial. Mungkin kamu sering ngerasa tegang, susah fokus, atau jadi gampang lelah.",
        "rekomendasi": [
            "Coba teknik relaksasi secara rutin. Misalnya, tarik napas dalam-dalam selama 4 detik, tahan 4 detik, lalu hembuskan pelan-pelan — ulangi 5x tiap pagi/sore.",
            "Kurangi paparan dari hal-hal yang bikin stres, misalnya terlalu lama di media sosial atau main game kompetitif berlebihan.",
            "Coba bicara ke orang dewasa yang kamu percaya, seperti orang tua, kakak, wali kelas, guru BK, atau pembimbing di sekolah/kampus. Kadang hanya dengan ngobrol, kamu bisa merasa lebih tenang dan mulai melihat jalan keluar dari masalah.",
            "Mulai cari tahu soal konseling atau psikolog sekolah/kampus. Nggak harus langsung terapi, cukup buat dapat wawasan cara ngatur kecemasan."
        ]
    },
    "Tinggi": {
        "deskripsi": "Gejala cemasmu cukup serius dan mungkin udah berdampak ke banyak aspek hidup, seperti sekolah, tidur, atau hubungan sosial. Kamu butuh perhatian dan dukungan lebih.",
        "rekomendasi": [
            "Jangan dipendam sendiri. Segera cari bantuan dari profesional seperti psikolog, konselor, atau guru BK.",
            "Kurangi hal-hal yang bikin makin stres, misalnya main game yang bikin emosi, debat online, atau tugas numpuk tanpa istirahat.",
            "Fokus pada kesehatan tubuh. Makan teratur, tidur minimal 7 jam, dan gerak ringan bisa bantu menurunkan level kecemasan.",
            "Kalau kamu merasa kehilangan arah, nggak apa-apa minta tolong. Itu bukan tanda lemah, tapi langkah cerdas untuk pulih."
        ]
    }
}

def generate_indicators(pred_label, user_input):
    desc = ''
    indicators = []

    # Ambil nilai penting
    spin_total = int(user_input.get('SPIN_T', 0))
    swl_total = int(user_input.get('SWL_T', 0))
    alasan = user_input.get('whyplay', '')
    jam_main = int(user_input.get('Hours', 0) or 0)
    nonton_stream = int(user_input.get('streams', 0) or 0)
    genre = user_input.get('Genre', '')
    ganggu = user_input.get('GADE', '').lower()
    playstyle = user_input.get('Playstyle', '')
    narc = int(user_input.get('Narcissism', 0) or 0)
    
    # Gabungkan beberapa indikator saling menguatkan
    if pred_label == 'Tinggi':
        if spin_total > 30:
            indicators.append(
                "Skor kecemasan sosial kamu sangat tinggi. "
                "Kamu mungkin sering merasa takut dinilai, gugup dalam situasi sosial, atau cenderung menghindari orang lain. "
                "Hal ini bisa sangat mempengaruhi kehidupan sehari-hari dan membuat kamu merasa terisolasi."
            )
        if swl_total < 15:
            indicators.append(
                "Kamu merasa hidupmu jauh dari yang kamu inginkan. "
                "Perasaan tidak puas ini bisa menyebabkan kamu gampang stres, kehilangan motivasi, dan mengalami kecemasan berkepanjangan."
            )
        if jam_main > 42:
            indicators.append(
                "Kamu menghabiskan waktu yang sangat lama untuk bermain game. "
                "Hal ini bisa mengganggu keseharian, mengurangi waktu tidur, dan memperparah kelelahan mental yang bisa memicu kecemasan tinggi."
            )
        if genre in ["FPS", "MOBA"]:
            indicators.append(
                "Genre game yang kamu mainkan termasuk tipe yang menuntut kompetisi tinggi. "
                "Kalau kamu bermain game seperti FPS atau MOBA secara intens, tekanan untuk menang, interaksi toksik, dan frustrasi saat kalah bisa memperparah kecemasan."
            )
        if alasan in ["melarikan diri dari kenyataan", "menghilangkan stres"]:
            indicators.append(
                "Kamu bermain game sebagai cara utama untuk lari dari kenyataan atau stres. "
                "Ini berisiko tinggi karena bukan menyelesaikan masalah, tapi justru bisa membuat kamu makin tertekan saat jauh dari game."
            )
        if genre in ["FPS", "MOBA"] and jam_main > 42 and alasan in ["melarikan diri dari kenyataan", "menghilangkan stres"]:
            indicators.append(
                "Kombinasi game kompetitif, waktu bermain berlebihan, dan tujuan bermain untuk pelarian menunjukkan kamu sedang mengalami tekanan yang besar. "
                "Kondisi ini bisa menjadi tanda kecemasan yang serius dan perlu perhatian lebih lanjut."
            )
        if spin_total > 30 and swl_total < 15 and alasan == "melarikan diri dari kenyataan":
            indicators.append(
                "Skor kecemasan sosial kamu tinggi, kamu tidak puas dengan kehidupanmu, dan kamu menggunakan game sebagai pelarian. "
                "Ini adalah kombinasi serius yang menunjukkan kamu berada dalam kondisi tekanan emosional yang berat. "
                "Kamu sangat disarankan untuk bicara dengan orang terpercaya atau tenaga profesional."
            )
            
    elif pred_label == 'Sedang':
        if spin_total > 30:
            indicators.append(
                "Kamu menunjukkan tanda-tanda kecemasan sosial yang cukup kuat. "
                "Bisa jadi kamu sering merasa gugup saat bertemu orang baru, susah ngomong di depan umum, atau cemas kalau dilihat banyak orang. "
                "Hal-hal ini bisa bikin kamu merasa lelah secara mental dan menarik diri dari lingkungan sosial."
            )
        if swl_total < 15:
            indicators.append(
                "Kamu mungkin merasa tidak puas dengan hidupmu saat ini. "
                "Mungkin ada hal penting yang kamu harapkan tapi belum tercapai, atau kamu merasa kehidupanmu nggak berjalan sesuai harapan. "
                "Rasa kecewa dan ketidakpuasan ini bisa memperbesar potensi munculnya kecemasan."
            )
        if jam_main > 42:
            indicators.append(
                "Kamu bermain game lebih dari 6 jam dalam sehari, dan itu bisa jadi terlalu berlebihan. "
                "Kalau ini dilakukan terus-menerus, bisa bikin kamu kelelahan, kurang istirahat, bahkan jadi susah fokus di hal lain. "
                "Kondisi kayak gini bisa jadi penyumbang rasa cemas yang makin meningkat."
            )
        if genre in ["FPS", "MOBA"]:
            indicators.append(
                "Kamu memilih genre game yang sifatnya kompetitif banget, seperti FPS atau MOBA. "
                "Game-game ini sering bikin pemain merasa tertekan buat menang, sering ketemu lingkungan yang toksik, dan bisa menimbulkan frustrasi. "
                "Ini bisa memperkuat tekanan psikologis yang kamu alami."
            )
        if alasan in ["melarikan diri dari kenyataan", "menghilangkan stres"]:
            indicators.append(
                "Kamu bermain game untuk ngurangin stres atau kabur dari tekanan hidup. "
                "Walaupun niatnya buat merasa lebih baik, tapi kalau ini jadi satu-satunya cara kamu menghindari masalah, justru bisa memperbesar kecemasan karena masalahnya tetap nggak selesai."
            )
        if genre in ["FPS", "MOBA"] and jam_main > 42 and alasan in ["melarikan diri dari kenyataan", "menghilangkan stres"]:
            indicators.append(
                "Kalau kamu main game kompetitif dalam waktu lama dan tujuannya buat kabur dari stres atau kenyataan, itu jadi kombinasi yang cukup berisiko. "
                "Tanpa disadari, kamu bisa makin terjebak dalam siklus stres yang datang dari luar dan dalam game sendiri."
            )
        if spin_total > 30 and swl_total < 15:
            indicators.append(
                "Tingkat kecemasan sosial kamu cukup tinggi dan kamu juga merasa nggak puas sama hidupmu. "
                "Dua hal ini bisa saling memperkuat dan bikin kamu lebih gampang ngerasa overthinking, cemas tanpa alasan jelas, atau menarik diri dari lingkungan sosial."
            )
    
    elif pred_label == 'Ringan':
        if alasan == "melarikan diri dari kenyataan":
            indicators.append(
                "Kamu bermain game buat ngelupain masalah atau kabur dari kenyataan. "
                "Walaupun kadang itu terasa menenangkan, tapi kalau terus-terusan, bisa bikin kamu jadi tergantung sama game buat ngatur emosi. "
                "Ini bisa jadi tanda awal bahwa kamu lagi stres atau punya tekanan yang belum terselesaikan."
            )
        elif spin_total > 25:
            indicators.append(
                "Kamu mungkin sering merasa gugup atau canggung saat berinteraksi sama orang lain. "
                "Ini bisa nunjukin adanya tanda-tanda kecemasan sosial ringan, yang kadang muncul waktu harus ngomong di depan umum, kenalan sama orang baru, atau cuma karena merasa diawasi."
            )
        elif swl_total < 20:
            indicators.append(
                "Kamu mungkin merasa belum puas sama kondisi hidupmu sekarang. "
                "Bisa jadi kamu lagi ngerasa kurang dihargai, kurang bahagia, atau belum capai apa yang kamu mau. "
                "Perasaan kayak gini bisa bikin kamu gampang cemas, walaupun belum sampai level yang berat."
            )
        elif 21 <= jam_main <= 42:
            indicators.append(
                "Kamu main game lumayan sering, tapi belum sampai berlebihan. "
                "Kalau waktu main ini jadi pelarian dari stres atau bikin kamu lupa waktu, sebaiknya mulai coba diatur lagi. "
                "Kebiasaan ini bisa jadi salah satu penyumbang rasa cemas kalau dibiarkan terus."
            )
        elif 5 <= nonton_stream <= 10:
            indicators.append(
                "Kamu cukup sering nonton konten game atau streaming. "
                "Kadang ini bisa jadi hiburan, tapi kalau terlalu sering bisa bikin kamu ngebandingin diri sama orang lain atau overthinking tentang performa di game. "
                "Hal ini secara nggak langsung bisa bikin kamu ngerasa nggak cukup atau jadi cemas."
            )
        elif alasan == "melarikan diri dari kenyataan" and spin_total > 25:
            indicators.append(
                "Kamu mungkin sedang berada di titik di mana interaksi sosial bikin kamu nggak nyaman, dan game kamu pakai sebagai cara buat menjauh dari tekanan itu. "
                "Gabungan ini bisa jadi awal dari kecemasan yang lebih dalam kalau nggak disadari dan dikendalikan."
            )
            
    elif pred_label == 'Rendah':
        if swl_total > 25 and ganggu == "tidak" and jam_main < 21:
            indicators.append(
                "Kamu menunjukkan keseimbangan hidup yang baik. "
                "Kepuasan hidup kamu tergolong tinggi, waktu main game juga nggak berlebihan, "
                "dan aktivitas penting seperti belajar atau kerja nggak terganggu. "
                "Ini semua jadi kombinasi kuat yang bantu kamu terhindar dari rasa cemas berlebihan."
            )
        elif swl_total > 25:
            indicators.append(
                "Kamu termasuk orang yang cukup puas dengan hidup kamu saat ini. "
                "Perasaan positif ini bikin kamu lebih kuat secara mental dan lebih tahan terhadap tekanan, "
                "makanya tingkat kecemasanmu tergolong rendah."
            )
        elif jam_main < 21 and ganggu == "tidak":
            indicators.append(
                "Waktu kamu bermain game masih dalam batas aman dan nggak sampai ganggu aktivitas utama seperti sekolah, kerja, atau kegiatan sehari-hari lainnya. "
                "Artinya kamu punya kontrol diri yang bagus dan tahu cara jaga keseimbangan antara hiburan dan tanggung jawab."
            )
        elif nonton_stream < 5:
            indicators.append(
                "Kamu nggak terlalu sering nonton streaming game, jadi waktu kamu nggak terlalu habis buat konsumsi konten digital. "
                "Ini bagus karena bisa bantu kamu tetap fokus sama hal-hal penting lain di luar dunia game."
            )
        elif narc <= 3:
            indicators.append(
                "Kamu punya ketertarikan yang sehat terhadap game. Artinya kamu suka main, tapi nggak sampai terlalu terobsesi. "
                "Ini bisa bantu menjaga keseimbangan hidup dan ngurangin risiko kecemasan."
            )

    # Gabungkan deskripsi akhir
    if indicators:
        desc += "\n"
        for i, teks in enumerate(indicators):
            if i == 0:
                desc += teks
            else:
                desc += " Selain itu, " + teks[0].lower() + teks[1:]
    else:
        desc += "Deskripsi: Data Anda menunjukkan hasil prediksi yang tidak mengindikasikan faktor dominan yang menonjol."

    return desc

def generate_swl_chart(swl_scores):
    swl_df = pd.DataFrame({
        "Pernyataan": [f"SWL{i+1}" for i in range(5)],
        "Skor": swl_scores
    })
    fig = px.bar(
        swl_df, x="Pernyataan", y="Skor",
        title="Skor Kuesioner SWLS per Pertanyaan",
        color="Skor", range_y=[1, 7],
        color_continuous_scale="Blues"
    )
    return fig.to_html(full_html=False)

def generate_spin_chart(spin_scores):
    pertanyaan = [f"SPIN{i+1}" for i in range(17)]
    df = pd.DataFrame({
        "Pertanyaan": pertanyaan,
        "Skor": spin_scores
    })

    fig = px.bar(
        df,
        x="Pertanyaan",
        y="Skor",
        title="Skor Kuesioner SPIN per Pertanyaan",
        color="Skor",
        range_y=[1, 5],
        color_continuous_scale="Reds"
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

def generate_gaming_pie_chart(jam_main, nonton_stream, antusiasme):
    labels = ['Jam Main', 'Streaming', 'Antusiasme (×10)']
    values = [jam_main, nonton_stream, antusiasme * 10]

    fig = px.pie(
        names=labels,
        values=values,
        title="Komposisi Intensitas Bermain Game",
        hole=0.4
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

def generate_indikator_chart(data):
    # Ambil nilai-nilai penting
    spin_total = int(data.get("SPIN_T", 0))
    swl_total = int(data.get("SWL_T", 0))
    jam_main = int(data.get("Hours", 0))
    nonton_stream = int(data.get("streams", 0))
    antusias = int(data.get("Narcissism", 0))

    indikator_scores_persen = {
        "SPIN Tinggi (Skor SPIN)": min(100, round((spin_total / 68) * 100)),
        "SWL Rendah (Skor SWLS)": 100 - min(100, round((swl_total / 35) * 100)),
        "Jam Main Game /minggu": min(100, round((jam_main / 42) * 100)),
        "Nonton Streaming /minggu": min(100, round((nonton_stream / 14) * 100)),
        "Antusias terhadap game": min(100, round((antusias / 5) * 100)),
    }

    indikator_df = pd.DataFrame({
        "Indikator": list(indikator_scores_persen.keys()),
        "Pengaruh (%)": list(indikator_scores_persen.values())
    }).sort_values("Pengaruh (%)", ascending=True)

    fig = px.bar(
        indikator_df,
        x="Pengaruh (%)",
        y="Indikator",
        orientation='h',
        color="Pengaruh (%)",
        color_continuous_scale="OrRd",
        range_x=[0, 100],
        title="Indikator Dominan"
    )

    return fig.to_html(full_html=False)

def generate_radar_chart(user_input):
    try:
        # Ambil nilai dari session/user_input
        spin = int(user_input.get("SPIN_T", 0))
        swl = int(user_input.get("SWL_T", 0))
        jam_main = int(user_input.get("Hours", 0))
        nonton_stream = int(user_input.get("streams", 0))
        antusias = int(user_input.get("Narcissism", 0))

        # Radar data
        radar_labels = [
            'Kecemasan Sosial (SPIN)', 
            'Kepuasan Hidup (SWLS)', 
            'Jam Main Game', 
            'Streaming Game', 
            'Antusiasme', 
            'Intensitas Total'
        ]
        radar_values = [
            min(100, spin / 68 * 100),
            min(100, swl / 35 * 100),
            min(100, jam_main / 42 * 100),
            min(100, nonton_stream / 14 * 100),
            min(100, antusias / 5 * 100),
            min(100, (jam_main + nonton_stream) / 56 * 100)
        ]

        # Buat radar chart
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill='toself',
            name='Profil Kamu',
            line=dict(color='rgb(61, 141, 122)')
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

        return pio.to_html(fig, full_html=False)
    
    except Exception as e:
        return f"<p style='color:red;'>Gagal menampilkan grafik radar: {str(e)}</p>"
    
def generate_gad_score_from_label(pred_label):
    if pred_label == "Rendah":
        return random.randint(0, 4)
    elif pred_label == "Ringan":
        return random.randint(5, 9)
    elif pred_label == "Sedang":
        return random.randint(10, 14)
    elif pred_label == "Tinggi":
        return random.randint(15, 21)
    else:
        return None