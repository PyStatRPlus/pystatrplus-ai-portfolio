<p align="center">
  <img src="docs/screenshots/logo.png" alt="PyStatR+ Logo" width="180"/>
</p>

<h1>🚀 PyStatR+ AI Portfolio Builder</h1>

<p>
AI-powered consulting portfolio builder for professionals, clients, and organizations.<br>
This app is built and maintained by <strong>PyStatR+</strong> to help transform expertise into polished, client-ready portfolios with branding, strategy, and export features.

## 📄 Release Notes

See detailed updates in the [Release Notes](docs/release_notes.md).

</p>

<p align="center">
  <img src="docs/screenshots/app_preview.png" alt="App Screenshot" width="600"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python">
  <img src="https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit">
  <img src="https://img.shields.io/badge/ReportLab-PDF-green">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img src="https://img.shields.io/badge/Status-Active-success">
</p>

<p><em>Futuristic Streamlit app</em> for building professional consulting portfolios,<br>
powered by <strong>PyStatR+</strong> branding, AI-driven content generation, and PDF exports.
</p>

<blockquote><em>Elevating Expertise into Professional Impact — Powered by PyStatR+</em></blockquote>

<hr>

<h2>✨ Features</h2>
<ul>
  <li>🔐 <strong>Secure Authentication</strong> (Admin & Client roles with password overrides)</li>
  <li>🛠️ <strong>Admin Dashboard</strong>
    <ul>
      <li>Password management</li>
      <li>Branding presets</li>
      <li>Client theme settings</li>
    </ul>
  </li>
  <li>👤 <strong>Client Dashboard</strong>
    <ul>
      <li>Locked PyStatR+ branding</li>
      <li>Simple portfolio creation</li>
    </ul>
  </li>
  <li>🎨 <strong>Brand Identity Workshop</strong> (logos, colors, fonts, themes)</li>
  <li>📝 <strong>Content Composer</strong> (summary, risks, opportunities, scenarios, insights)</li>
  <li>👁️ <strong>Live Preview</strong> before export</li>
  <li>📄 <strong>Professional PDF Export</strong> (Light/Dark themes, watermark, branding)</li>
</ul>

<hr>

<h2>🛠️ Installation & Deployment</h2>

<h3>Local Setup</h3>
<ol>
  <li><strong>Clone the repository</strong>
    <pre><code>git clone https://github.com/your-username/pystatrplus-ai-portfolio.git
cd pystatrplus-ai-portfolio</code></pre>
  </li>
  <li><strong>Create and activate a virtual environment</strong>
    <pre><code>uv venv
source .venv/bin/activate</code></pre>
  </li>
  <li><strong>Install dependencies</strong>
    <pre><code>uv tool add -r requirements.txt</code></pre>
  </li>
  <li><strong>Run the app</strong>
    <pre><code>uv run streamlit run app.py</code></pre>
  </li>
</ol>

<h3>Deploying to Streamlit Cloud</h3>
<ol>
  <li>Push your repo to GitHub.</li>
  <li>Go to ☁️ <a href="https://streamlit.io/cloud">Streamlit Cloud</a>.</li>
  <li>Connect your repo and deploy.</li>
  <li>Ensure you include:
    <ul>
      <li><code>requirements.txt</code></li>
      <li><code>runtime.txt</code> → <code>python-3.12</code></li>
      <li><code>branding_presets.json</code> (optional, auto-created)</li>
      <li><code>admin_settings.json</code> (optional, auto-created)</li>
      <li><code>.streamlit/secrets.toml</code> (⚠️ not pushed to GitHub)</li>
    </ul>
  </li>
</ol>

<hr>

<h2>🔐 Secrets Configuration</h2>
<p>Create a <code>.streamlit/secrets.toml</code> file (not committed to GitHub).</p>

<pre><code>[users]
alierwai_password = "your_admin_password"
client1_password = "client1_pass"
client2_password = "client2_pass"
</code></pre>

<hr>

<h2>🎯 Usage</h2>

<h3>🔑 Login</h3>
<ul>
  <li>Enter your username: <code>alierwai</code>, <code>client1</code>, or <code>client2</code></li>
  <li>Enter your password (from <code>secrets.toml</code> or admin override)</li>
</ul>

<h3>🛠️ Admin Dashboard</h3>
<ul>
  <li>Password management (overrides & resets)</li>
  <li>Branding presets (logo, color, typography)</li>
  <li>Content builder & live preview</li>
  <li>Export polished, branded PDFs</li>
</ul>

<h3>👤 Client Dashboard</h3>
<ul>
  <li>Locked PyStatR+ branding</li>
  <li>Add project details, opportunities, risks, scenarios</li>
  <li>Upload optional images</li>
  <li>Export professional portfolio PDF</li>
</ul>

<h3>📄 PDF Export</h3>
<ul>
  <li>Branded cover page</li>
  <li>Section dividers & tables</li>
  <li>Auto watermark (logo or text)</li>
  <li>Closing thank-you page</li>
</ul>

<hr>

<h2>🗺️ Roadmap</h2>
<ul>
  <li><strong>🚀 Short-term (v1.x)</strong>
    <ul>
      <li>Multi-client admin management</li>
      <li>Rich text editor</li>
      <li>Theme preview toggle</li>
      <li>Expanded branding presets</li>
    </ul>
  </li>
  <li><strong>🌐 Medium-term (v2.x)</strong>
    <ul>
      <li>AI-assisted content drafting</li>
      <li>Portfolio analytics</li>
      <li>Multi-language export</li>
      <li>Team collaboration mode</li>
    </ul>
  </li>
  <li><strong>🔮 Long-term (v3.x+)</strong>
    <ul>
      <li>Cloud storage integration</li>
      <li>Custom industry PDF templates</li>
      <li>AI design assistant</li>
      <li>SaaS platform with subscription tiers</li>
    </ul>
  </li>
</ul>

<hr>

<h2>📜 License</h2>
<p>
This project is licensed under the 📜 <a href="https://opensource.org/licenses/MIT">MIT License</a>.<br>
You are free to use, modify, and distribute the code with attribution.
</p>

<p>⚠️ Note: The <strong>PyStatR+</strong> brand name, logo, and branding elements are proprietary and not covered by this license.</p>

<hr>

<h2>🤝 Contributions</h2>
<p>
External contributions are welcome but not required.<br>
PyStatR+ leads official development and long-term support.<br>
If you’d like to suggest improvements, feel free to open an issue or submit a pull request.
</p>

<hr>

<h2>💡 About PyStatR+</h2>
<p>
<strong>PyStatR+</strong> is an educational data-science initiative founded in 2024 to bridge the gap between academic statistics and real-world data science.<br>
Focused on healthcare analytics, mentorship, and practical applications of Python, R, and statistics, PyStatR+ empowers professionals to build impactful careers and deliver data-driven results.
</p>

<h2>📄 Release Notes</h2> <div class="card"> <p>See detailed updates in the <a href="docs/release_notes.md">Release Notes</a>.</p> </div>