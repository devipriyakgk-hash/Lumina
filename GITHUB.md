# Put Lumina on GitHub

Do this on your computer (or tell me your GitHub username and I can fill it in).

## 1. Create the empty repo

1. Log in at https://github.com
2. Click **New repository**
3. Name: `lumina`
4. Public (for a portfolio)
5. **Do not** add a README, .gitignore, or license (this project already has them)
6. Click **Create repository**

## 2. Upload this project

Replace `YOUR_USERNAME` with your GitHub username.

```bash
git remote add origin https://github.com/YOUR_USERNAME/lumina.git
git branch -M main
git push -u origin main
```

GitHub will ask you to log in. Use a **Personal Access Token** as the password  
(GitHub → Settings → Developer settings → Personal access tokens).

If you already added `origin` once:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/lumina.git
git push -u origin main
```

## 3. After it uploads

On the GitHub page, check that these show:

- `README.md`
- `src/auditor.py`
- `app.py`
- `public/`

Then in the repo **About** box, add:

> Static accessibility checker — paste a URL, get a scored, plain-language report.

---

Send me your **GitHub username** if you want the commands filled in for you.
