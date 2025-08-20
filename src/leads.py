leads = []
if request.method == "POST":
    f = request.files.get("file")
    if not f:
        flash("No file provided", "danger")
        return redirect(url_for("leads.leads_home"))

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in UPLOAD_EXT:
        flash("Unsupported file type", "danger")
        return redirect(url_for("leads.leads_home"))

    save_path = os.path.join(upload_dir, secure_filename(f.filename))
    f.save(save_path)

    if ext == ".csv":
        df = pd.read_csv(save_path)
    else:
        df = pd.read_excel(save_path)

    df = normalize_columns(df)

    # Save accepted only (no validation yet)
    df.to_csv(accepted_path, index=False)

    flash(f"Imported {len(df)} leads.", "success")

if os.path.exists(accepted_path):
    with open(accepted_path, newline="") as f_in:
        reader = csv.DictReader(f_in)
        leads = list(reader)

return render_template("leads.html", leads=leads)
