// Theme switching functionality
window.dash_clientside = Object.assign({}, window.dash_clientside, {
	theme: {
		toggleTheme: function (theme, toggle_clicks) {
			let storedTheme = localStorage.getItem('theme');
			if (!storedTheme) {
				storedTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
			}
			let currentTheme = storedTheme;
			if (toggle_clicks && toggle_clicks > 0) {
				currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
			}
			document.documentElement.setAttribute('data-theme', currentTheme);
			localStorage.setItem('theme', currentTheme);
			return currentTheme;
		}
	}
});
