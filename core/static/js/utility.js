
function toggleExpand(el) {
    const fullText = el.getAttribute('data-full');
    const isExpanded = el.getAttribute('data-expanded') === 'true';
    if (isExpanded) {
    el.textContent = fullText.slice(0, 200) + '...';
    el.setAttribute('data-expanded', 'false');
    } else {
    el.textContent = fullText;
    el.setAttribute('data-expanded', 'true');
    }
}

function setupExpandableText() {
    document.querySelectorAll('[data-expandable]').forEach(el => {
    const text = el.textContent.trim();
    if (text.length > 200) {
        el.setAttribute('data-full', text);
        el.textContent = text.slice(0, 200) + '...';
        el.setAttribute('data-expanded', 'false');
        el.classList.add('cursor-pointer');
        el.addEventListener('click', () => toggleExpand(el));
    }
    });
    console.log("Expandable text set up for elements:", document.querySelectorAll('[data-expandable]'));
}

//document.addEventListener('DOMContentLoaded', () =>{ console.log("expandable set up"); setupExpandableText() });
