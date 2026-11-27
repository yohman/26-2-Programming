/* Preview the released, unanswered quiz using the course Markdown renderer. */
(async () => {
  const archive = document.querySelector('[data-quiz-archive]');
  if (!archive) return; // The course release gate removed the archive.
  const preview = archive.querySelector('[data-quiz-preview]');
  try {
    const response = await fetch(archive.querySelector('.quiz-download').href);
    if (!response.ok) throw new Error('Quiz unavailable');
    const notebook = await response.json();
    preview.innerHTML = notebook.cells.filter(cell => cell.cell_type === 'markdown')
      .map(cell => '<section>' + markdownHtml(Array.isArray(cell.source) ? cell.source.join('') : cell.source) + '</section>')
      .join('');
  } catch {
    preview.innerHTML = '<p role="status"><span class="ja">プレビューを読み込めません。上のNotebookをダウンロードしてください。</span><span class="en">The preview could not load. You can still download the notebook above.</span></p>';
  } finally {
    preview.removeAttribute('aria-busy');
  }
})();
