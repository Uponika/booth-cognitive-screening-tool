/*!
* Start Bootstrap - Business Frontpage v5.0.9 (https://startbootstrap.com/template/business-frontpage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-business-frontpage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

const cards = document.querySelectorAll('.card-animate');
const io = new IntersectionObserver(entries => {
entries.forEach(e => {
    if (e.isIntersecting) {
    e.target.style.animationPlayState = 'running';
    e.target.classList.add('in-view');
    io.unobserve(e.target);
    }
});
}, { threshold: 0.2 });

cards.forEach(c => {
// pause until observed
c.style.animationPlayState = 'paused';
io.observe(c);
});