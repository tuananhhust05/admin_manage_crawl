(() => {
    const formsRootId = 'forms';
    const addBtnId = 'add-article';
    const genBtnId = 'generate';
    const loaderId = 'loader';
    const outputId = 'output';

    let counter = 0;

    function createForm(id) {
        const card = document.createElement('div');
        card.className = 'as-card';

        const ta = document.createElement('textarea');
        ta.className = 'as-textarea';
        ta.placeholder = `Paste article #${id + 1} here...`;

        const actions = document.createElement('div');
        actions.className = 'as-actions';
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'as-btn as-btn-secondary';
        remove.textContent = 'Remove';
        remove.addEventListener('click', () => card.remove());

        actions.appendChild(remove);
        card.appendChild(ta);
        card.appendChild(actions);
        return card;
    }

    async function generate() {
        const loader = document.getElementById(loaderId);
        const output = document.getElementById(outputId);
        output.innerHTML = '';

        const formsRoot = document.getElementById(formsRootId);
        const texts = Array.from(formsRoot.querySelectorAll('textarea'))
            .map(el => (el.value || '').trim())
            .filter(v => v.length > 0);

        if (texts.length === 0) {
            output.innerHTML = '<div class="as-article">Please add at least one article.</div>';
            return;
        }

        loader.style.display = 'flex';
        try {
            const res = await fetch('/api/summarize-articles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ articles: texts })
            });
            const json = await res.json();
            if (!json.success) throw new Error(json.error || 'Failed');

            const summary = (json.data && json.data.summary) || '';
            if (!summary) {
                output.innerHTML = '<div class="as-article">No summary returned.</div>';
                return;
            }

            // Render summary as multi-paragraph article
            const article = document.createElement('div');
            article.className = 'as-article';

            const lines = summary.split(/\n\n+/).map(s => s.trim()).filter(Boolean);
            if (lines.length) {
                const first = document.createElement('h2');
                first.textContent = lines[0].replace(/^Title:\s*/i, '');
                article.appendChild(first);
                lines.slice(1).forEach(p => {
                    const para = document.createElement('p');
                    para.textContent = p;
                    article.appendChild(para);
                });
            } else {
                const para = document.createElement('p');
                para.textContent = summary;
                article.appendChild(para);
            }
            output.appendChild(article);
        } catch (e) {
            output.innerHTML = `<div class="as-article">Error: ${e.message}</div>`;
        } finally {
            loader.style.display = 'none';
        }
    }

    function init() {
        const formsRoot = document.getElementById(formsRootId);
        const addBtn = document.getElementById(addBtnId);
        const genBtn = document.getElementById(genBtnId);
        if (!formsRoot || !addBtn || !genBtn) return;

        const addForm = () => {
            const form = createForm(counter++);
            formsRoot.appendChild(form);
        };

        addBtn.addEventListener('click', addForm);
        genBtn.addEventListener('click', generate);

        // initial form
        addForm();
    }

    window.ArticleSummarizer = { init };
})();


