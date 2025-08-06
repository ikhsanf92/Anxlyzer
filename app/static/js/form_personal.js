document.addEventListener("DOMContentLoaded", function () {
const ageInput = document.querySelector('input[name="Age"]');
const degreeSelect = document.querySelector('select[name="Degree"]');

const optionsByAge = (age) => {
    if (age === 12 ) {
    return ["Lainnya"];
    } else if (age >= 13 && age <= 15) {
    return ["SD", "Lainnya"];
    } else if (age >= 16 && age <= 18) {
    return ["SD", "SMP", "Lainnya"];
    } else if (age >= 19 && age <= 22) {
    return ["SD", "SMP", "SMA/Sederajat", "Lainnya"];
    } else if (age <= 25) {
    return ["SD", "SMP", "SMA/Sederajat", "Sarjana", "Lainnya"];
    } else {
    return ["Lainnya"];
    }
};

ageInput.addEventListener("input", () => {
    const age = parseInt(ageInput.value);
    if (!age || age < 12 || age > 25) return;

    // Simpan value saat ini jika ada
    const current = degreeSelect.value;

    // Kosongkan pilihan
    degreeSelect.innerHTML = '<option value="" disabled selected>Pilih pendidikan</option>';

    // Tambahkan opsi baru
    optionsByAge(age).forEach((option) => {
    const opt = document.createElement("option");
    opt.value = option;
    opt.textContent = option;
    degreeSelect.appendChild(opt);
    });

    // Pilih kembali jika masih valid
    if (optionsByAge(age).includes(current)) {
    degreeSelect.value = current;
    }
});
});