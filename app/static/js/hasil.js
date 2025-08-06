let currentSlide = 0;
let infoCarousel_current = 0;
let infoCarousel_total = 0;

function infoCarousel_update() {
const wrapper = document.getElementById('infoCarousel_wrapper');
const slides = wrapper.querySelectorAll(':scope > div'); // Hitung jumlah slide aktual
infoCarousel_total = slides.length;
// Sembunyikan atau tampilkan dot terakhir sesuai jumlah slide
const dot3 = document.getElementById('infoCarousel_dot3');
if (dot3) {
    dot3.classList.toggle('hidden', infoCarousel_total < 4);
}

wrapper.style.transform = `translateX(-${infoCarousel_current * 100}%)`;

// Update dot navigasi jika ada
for (let i = 0; i < infoCarousel_total; i++) {
    const dot = document.getElementById(`infoCarousel_dot${i}`);
    if (dot) {
    dot.classList.remove("bg-emerald-600", "scale-125");
    dot.classList.add("bg-gray-300", "scale-100");
    }
}

const activeDot = document.getElementById(`infoCarousel_dot${infoCarousel_current}`);
if (activeDot) {
    activeDot.classList.remove("bg-gray-300", "scale-100");
    activeDot.classList.add("bg-emerald-600", "scale-125");
}

// Show/hide prev/next button
const prevBtn = document.getElementById('infoCarousel_prevBtn');
const nextBtn = document.getElementById('infoCarousel_nextBtn');

if (prevBtn && nextBtn) {
    prevBtn.classList.toggle('invisible', infoCarousel_current === 0);
    nextBtn.classList.toggle('invisible', infoCarousel_current >= infoCarousel_total - 1);
}
}

function infoCarousel_nextSlide() {
if (infoCarousel_current < infoCarousel_total - 1) {
    infoCarousel_current++;
    infoCarousel_update();
}
}

function infoCarousel_prevSlide() {
if (infoCarousel_current > 0) {
    infoCarousel_current--;
    infoCarousel_update();
}
}

function showSlide(index) {
const wrapper = document.getElementById('carousel-content');
const totalSlides = wrapper.children.length;
if (index < 0) index = totalSlides - 1;
if (index >= totalSlides) index = 0;
currentSlide = index;
wrapper.style.transform = `translateX(-${index * 100}%)`;
}

function prevSlide() {
showSlide(currentSlide - 1);
}

function nextSlide() {
showSlide(currentSlide + 1);
}

function showModal(id, contentId) {
const modal = document.getElementById(id);
const content = document.getElementById(contentId);
modal.classList.remove('hidden');
setTimeout(() => {
    content.classList.remove('scale-95', 'opacity-0');
    content.classList.add('scale-100', 'opacity-100');
}, 50);
showSlide(0);
}

function hideModal(id, contentId) {
const modal = document.getElementById(id);
const content = document.getElementById(contentId);
content.classList.remove('scale-100', 'opacity-100');
content.classList.add('scale-95', 'opacity-0');
setTimeout(() => {
    modal.classList.add('hidden');
}, 300);
}

function openModal() {
document.getElementById("chartModal").classList.remove("hidden");
showSlide(0);
}

function closeModal() {
document.getElementById("chartModal").classList.add("hidden");
}

function toggleModal(id) {
const modal = document.getElementById(id);
modal.classList.toggle('hidden');
}

window.addEventListener('DOMContentLoaded', () => {
infoCarousel_update();

// Attach events to buttons manually
const nextBtn = document.getElementById('infoCarousel_nextBtn');
const prevBtn = document.getElementById('infoCarousel_prevBtn');

if (nextBtn) nextBtn.onclick = infoCarousel_nextSlide;
if (prevBtn) prevBtn.onclick = infoCarousel_prevSlide;
});