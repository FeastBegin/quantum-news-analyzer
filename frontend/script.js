document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const newsInput = document.getElementById('newsInput');
    const resultsSection = document.getElementById('resultsSection');
    const mockWarning = document.getElementById('mockWarning');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    
    // Result elements
    const hypeFill = document.getElementById('hypeFill');
    const hypeScoreText = document.getElementById('hypeScoreText');
    const valRealism = document.getElementById('valRealism');
    const valTimeline = document.getElementById('valTimeline');
    const valExaggeration = document.getElementById('valExaggeration');
    const summaryText = document.getElementById('summaryText');
    const keywordsContainer = document.getElementById('keywordsContainer');
    
    // News elements
    const newsLoading = document.getElementById('newsLoading');
    const newsContainer = document.getElementById('newsContainer');

    analyzeBtn.addEventListener('click', async () => {
        const text = newsInput.value.trim();
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }

        // UI Loading state
        analyzeBtn.disabled = true;
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Analysis failed');
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert(`Error analyzing text: ${error.message}`);
        } finally {
            // Restore UI
            analyzeBtn.disabled = false;
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    });

    function displayResults(data) {
        resultsSection.classList.remove('hidden');
        
        if (data.is_mock) {
            mockWarning.classList.remove('hidden');
        } else {
            mockWarning.classList.add('hidden');
        }

        // Animate gauge
        setTimeout(() => {
            const percentage = (data.hype_score * 100).toFixed(0);
            hypeFill.style.width = `${percentage}%`;
            hypeScoreText.textContent = `${percentage}%`;
            
            // Color based on score
            if (data.hype_score > 0.7) {
                hypeScoreText.style.color = '#ef4444'; // Red
            } else if (data.hype_score < 0.4) {
                hypeScoreText.style.color = '#10b981'; // Green
            } else {
                hypeScoreText.style.color = '#f59e0b'; // Yellow
            }
        }, 100);

        // Set features
        animateValue(valRealism, 0, data.features[0], 1000);
        animateValue(valTimeline, 0, data.features[1], 1000);
        animateValue(valExaggeration, 0, data.features[2], 1000);

        // Set summary
        summaryText.textContent = data.summary;
        
        // Set keywords
        keywordsContainer.innerHTML = '';
        if (data.keywords && data.keywords.length > 0) {
            data.keywords.forEach(kw => {
                const span = document.createElement('span');
                span.className = 'keyword-tag';
                span.textContent = kw;
                keywordsContainer.appendChild(span);
            });
        }
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = (start + (end - start) * easeOutQuart).toFixed(2);
            obj.innerHTML = current;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    async function fetchRecentNews() {
        try {
            const response = await fetch('/api/news');
            if (!response.ok) throw new Error('Failed to fetch news');
            
            const newsItems = await response.json();
            newsLoading.classList.add('hidden');
            
            if (newsItems.length === 0) {
                newsContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No recent news found.</p>';
                return;
            }

            newsItems.forEach(item => {
                const card = document.createElement('div');
                card.className = 'news-card';
                
                let hypeClass = 'hype-low';
                let hypeText = 'Low Hype';
                if (item.hype_score > 0.7) {
                    hypeClass = 'hype-high';
                    hypeText = 'High Hype';
                } else if (item.hype_score > 0.4) {
                    hypeClass = 'hype-med';
                    hypeText = 'Med Hype';
                }

                // Format keywords
                const kws = item.keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join('');

                card.innerHTML = `
                    <div class="news-meta">
                        <span>${new Date(item.date).toLocaleDateString()}</span>
                        <span class="news-hype ${hypeClass}">${hypeText} (${(item.hype_score*100).toFixed(0)}%)</span>
                    </div>
                    <a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.title}</a>
                    <p class="news-summary">${item.summary}</p>
                    <div class="keywords-container" style="margin-bottom: 0;">
                        ${kws}
                    </div>
                `;
                newsContainer.appendChild(card);
            });
        } catch (error) {
            console.error('Error fetching news:', error);
            newsLoading.textContent = 'Failed to load recent news.';
        }
    }

    // Initial fetch
    fetchRecentNews();
});
