def process_population_loans(session: Session, frame: DataFrame):
    date_frame: DataFrame = frame.iloc[11:-5, 0:2]

    total_loans_data = frame.iloc[11:-5, 2:14]
    total_loans_data[14] = Series()
    process_table(session, date_frame, total_loans_data, TotalLoans)

    housing_loans_data = frame.iloc[11:-5, 14:27]
    process_table(session, date_frame, housing_loans_data, HousingLoans)

    consumer_loans_data = frame.iloc[11:-5, 27:40]
    process_table(session, date_frame, consumer_loans_data, ConsumerLoans)

    cash_loans_data = frame.iloc[11:-5, 40:53]
    process_table(session, date_frame, cash_loans_data, CashLoans)

    other_loans_data = frame.iloc[11:-5, 53:66]
    process_table(session, date_frame, other_loans_data, OtherLoans)