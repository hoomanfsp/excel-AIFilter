import pandas as pd

def create_mock_excel(filename="test_data.xlsx"):
    data = {
        "ID": range(1, 61),
        "University": [
            "MIT", "Stanford", "Harvard", "Caltech", "Oxford", "Cambridge", "UCL", "Imperial", "ETH Zurich", "Chicago",
            "Yale", "Princeton", "Penn", "Columbia", "Cornell", "Johns Hopkins", "Michigan", "Toronto", "NUS", "Tsinghua",
            "Peking", "Tokyo", "Seoul National", "Melbourne", "Sydney", "UNSW", "Kyoto", "HKU", "McGill", "UBC",
            "UCLA", "UC Berkeley", "UC San Diego", "Washington", "NYU", "Duke", "Northwestern", "Brown", "Dartmouth", "Vanderbilt",
            "Rice", "Washington University", "Notre Dame", "Georgetown", "Emory", "Carnegie Mellon", "USC", "Virginia", "UNC", "Wake Forest",
            "Tufts", "Florida", "Texas", "Wisconsin", "UIUC", "Georgia Tech", "Purdue", "Ohio State", "Maryland", "Rutgers"
        ],
        "Program": [
            "Computer Science", "Mechanical Engineering", "History", "Physics", "Philosophy", "Mathematics", "Medicine", "Biology", "Chemistry", "Economics",
            "Law", "Political Science", "Business", "Journalism", "Architecture", "Nursing", "Education", "Psychology", "Sociology", "Anthropology",
            "Linguistics", "Literature", "Art History", "Music", "Theater", "Film Studies", "Design", "Environmental Science", "Geography", "Geology",
            "Astronomy", "Statistics", "Data Science", "Information Systems", "Cybersecurity", "Software Engineering", "Artificial Intelligence", "Robotics", "Biomedical Engineering", "Chemical Engineering",
            "Civil Engineering", "Electrical Engineering", "Aerospace Engineering", "Materials Science", "Industrial Engineering", "Operations Research", "Finance", "Accounting", "Marketing", "Management",
            "Human Resources", "Supply Chain", "Public Health", "Social Work", "Public Policy", "International Relations", "Urban Planning", "Criminology", "Theology", "Sports Management"
        ],
        "Location": [
            "USA", "USA", "USA", "USA", "UK", "UK", "UK", "UK", "Switzerland", "USA",
            "USA", "USA", "USA", "USA", "USA", "USA", "USA", "Canada", "Singapore", "China",
            "China", "Japan", "South Korea", "Australia", "Australia", "Australia", "Japan", "Hong Kong", "Canada", "Canada",
            "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA",
            "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA",
            "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA"
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Created {filename} with {len(df)} rows.")

if __name__ == "__main__":
    create_mock_excel()
