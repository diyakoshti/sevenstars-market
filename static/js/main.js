const toggle = document.querySelector(".nav-toggle");
const links = document.querySelector(".nav-links");
if (toggle && links) toggle.addEventListener("click", () => links.classList.toggle("open"));

document.querySelectorAll(".message").forEach((message) => {
  setTimeout(() => message.classList.add("hide"), 4500);
});
