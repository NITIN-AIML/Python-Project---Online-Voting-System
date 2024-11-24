from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

class Election:
    def __init__(self):
        self.voters_df = pd.DataFrame(columns=["Name", "Age", "Voter_ID", "PIN", "Has_Voted", "Voted_For"])
        self.candidates_df = pd.DataFrame(columns=["Name", "Votes"])
        self.total_votes = 0

    def add_candidate(self, name):
        self.candidates_df = pd.concat(
            [self.candidates_df, pd.DataFrame({"Name": [name], "Votes": [0]})],
            ignore_index=True,
        )

    def add_voter(self, name, age, voter_id, pin):
        self.voters_df = pd.concat(
            [
                self.voters_df,
                pd.DataFrame(
                    {
                        "Name": [name],
                        "Age": [age],
                        "Voter_ID": [voter_id],
                        "PIN": [pin],
                        "Has_Voted": [False],
                        "Voted_For": [None],
                    }
                ),
            ],
            ignore_index=True,
        )

    def vote(self, voter_id, candidate_name, entered_pin):
        voter = self.voters_df.loc[self.voters_df["Voter_ID"] == voter_id]
        if voter.empty:
            return "❌ Voter not registered."

        if voter.iloc[0]["Has_Voted"]:
            return "❌ You have already voted. Voting again is not allowed."

        if voter.iloc[0]["PIN"] != entered_pin:
            return "❌ Invalid PIN. Please try again."

        candidate_idx = self.candidates_df[self.candidates_df["Name"] == candidate_name].index
        if candidate_idx.empty:
            return "❌ Candidate does not exist."

        self.candidates_df.at[candidate_idx[0], "Votes"] += 1
        self.voters_df.loc[self.voters_df["Voter_ID"] == voter_id, ["Has_Voted", "Voted_For"]] = [True, candidate_name]
        self.total_votes += 1
        return f"✅ Vote successfully cast for {candidate_name}."

    def get_candidates(self):
        return self.candidates_df[['Name']].to_dict(orient='records')

    def get_results(self):
        return self.candidates_df.to_dict(orient='records')


# Initialize Election system
election = Election()
election.add_candidate("AAP")
election.add_candidate("CONG")
election.add_candidate("NOTA")

voter_data = [
    ("Aayush", 25, "FHJ123456789", 63486),
    ("Dilip", 30, "JGH987654321", 73479),
    ("Rohan", 26, "AHD789012345", 95874),
]

for name, age, voter_id, pin in voter_data:
    election.add_voter(name, age, voter_id, pin)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_voter():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        voter_id = request.form['voter_id']
        pin = int(request.form['pin'])

        election.add_voter(name, age, voter_id, pin)
        flash('You have successfully registered to vote!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        try:
            pin = int(request.form['pin'])
        except ValueError:
            flash("❌ Invalid PIN format. Please enter numeric PIN.", 'danger')
            return redirect(url_for('vote'))

        candidate_name = request.form['candidate']

        result = election.vote(voter_id, candidate_name, pin)
        flash(result, 'info')

        return redirect(url_for('vote'))

    candidates = election.get_candidates()
    return render_template('vote.html', candidates=candidates)


@app.route('/results')
def results():
    election_results = election.get_results()
    return render_template('results.html', election_results=election_results)


if __name__ == "__main__":
    app.run(debug=True)
