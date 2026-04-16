document.addEventListener("DOMContentLoaded", () => {
    const hasAnime = typeof anime !== "undefined";

    const animateInElements = document.querySelectorAll(".animate-in");
    if (hasAnime && animateInElements.length) {
        anime({
            targets: animateInElements,
            opacity: [0, 1],
            translateY: [20, 0],
            duration: 650,
            easing: "easeOutExpo",
            delay: anime.stagger(85),
        });
    }

    const staggerGroups = document.querySelectorAll(".animate-stagger");
    if (hasAnime) {
        staggerGroups.forEach((group) => {
            anime({
                targets: group.children,
                opacity: [0, 1],
                translateY: [24, 0],
                scale: [0.98, 1],
                duration: 700,
                easing: "easeOutExpo",
                delay: anime.stagger(90),
            });
        });
    }

    const bars = document.querySelectorAll(".animate-bar");
    bars.forEach((bar) => {
        const width = Number(bar.dataset.width || 0);
        bar.style.width = "0%";
        if (hasAnime) {
            anime({
                targets: bar,
                width: `${width}%`,
                duration: 1200,
                easing: "easeOutCubic",
                delay: 180,
            });
        } else {
            requestAnimationFrame(() => {
                bar.style.width = `${width}%`;
            });
        }
    });

    const counters = document.querySelectorAll(".count-up");
    counters.forEach((counter) => {
        const target = Number(counter.dataset.count || 0);
        if (!Number.isFinite(target)) {
            return;
        }
        if (hasAnime) {
            const state = { value: 0 };
            anime({
                targets: state,
                value: target,
                round: 1,
                duration: 1300,
                easing: "easeOutExpo",
                delay: 100,
                update: () => {
                    counter.textContent = state.value.toLocaleString("es-CO");
                },
            });
        } else {
            counter.textContent = target.toLocaleString("es-CO");
        }
    });

    const tabs = document.querySelectorAll(".tab-link, .tab-item");
    tabs.forEach((tab) => {
        tab.addEventListener("mouseenter", () => {
            if (!hasAnime) {
                return;
            }
            anime.remove(tab);
            anime({
                targets: tab,
                translateY: [-1, 0],
                duration: 260,
                easing: "easeOutSine",
            });
        });
    });
});
