from app.data.init import conn, curs
from app.exception.database import RecordNotFound
from app.model.report import Report


# -------------------------------
#   Table1 creation
# -------------------------------


curs.execute("""
             create table if not exists reports(
                 report_id text primary key,
                 assessment_id text references assessments( assessment_id ),
                 public integer default 0,
                 key text,
                 report_name text,
                 summary text,
                 recommendation_title_1 text,
                 recommendation_content_1 text,
                 recommendation_title_2 text,
                 recommendation_content_2 text,
                 recommendation_title_3 text,
                 recommendation_content_3 text
                 )
             """)


# -------------------------------
#   Helper functions
# -------------------------------

def report_row_to_model(row: tuple) -> Report:

     report_id, \
     assessment_id, \
     public, \
     key, \
     report_name, \
     summary, \
     recommendation_title_1, \
     recommendation_content_1, \
     recommendation_title_2, \
     recommendation_content_2, \
     recommendation_title_3, \
     recommendation_content_3 = row

     return Report(
             report_id=report_id,
             assessment_id=assessment_id,
             public=public,
             key=key,
             report_name=report_name,
             summary=summary,
             recommendation_title_1=recommendation_title_1,
             recommendation_content_1=recommendation_content_1,
             recommendation_title_2=recommendation_title_2,
             recommendation_content_2=recommendation_content_2,
             recommendation_title_3=recommendation_title_3,
             recommendation_content_3=recommendation_content_3 
             )


# -------------------------------
#   CRUDS
# -------------------------------

def create_report(report: Report) -> Report:

    qry = """insert into
    reports(
            report_id,
            assessment_id,
            key,
            report_name,
            summary,
            recommendation_title_1,
            recommendation_content_1,
            recommendation_title_2,
            recommendation_content_2,
            recommendation_title_3,
            recommendation_content_3
            )
    values(
            :report_id,
            :assessment_id,
            :key,
            :report_name,
            :summary,
            :recommendation_title_1,
            :recommendation_content_1,
            :recommendation_title_2,
            :recommendation_content_2,
            :recommendation_title_3,
            :recommendation_content_3
            )
    """

    cursor = conn.cursor()
    try:
        cursor.execute(qry, report.model_dump())
        conn.commit()
        return report
    finally:
        cursor.close()

def get_report(report_id: str) -> Report:

    qry = """
    select 
        report_id,
        assessment_id,
        public,
        key,
        report_name,
        summary,
        recommendation_title_1,
        recommendation_content_1,
        recommendation_title_2,
        recommendation_content_2,
        recommendation_title_3,
        recommendation_content_3
    from
        reports
    where
        report_id = :report_id
    """

    cursor = conn.cursor()
    try:
        cursor.execute(qry, {"report_id":report_id})
        row = cursor.fetchone()
        return report_row_to_model(row)
    finally:
        cursor.close()


def get_all_reports() -> list[Report]:

    qry = """
    select 
        report_id,
        assessment_id,
        public,
        key,
        report_name,
        summary,
        recommendation_title_1,
        recommendation_content_1,
        recommendation_title_2,
        recommendation_content_2,
        recommendation_title_3,
        recommendation_content_3
    from
        reports
    """
    cursor = conn.cursor()
    try:
        cursor.execute(qry)
        rows = cursor.fetchall()
        if rows:
            return [report_row_to_model(row) for row in rows]
        else:
            return []
    finally:
        cursor.close() 


def update_report(report: Report) -> Report:

    qry = """
    update
        reports
    set
        assessment_id = :assessment_id,
        key = :key,
        report_name = :report_name,
        summary = :summary,
        recommendation_title_1 = :recommendation_title_1,
        recommendation_content_1 = :recommendation_content_1,
        recommendation_title_2 = :recommendation_title_2,
        recommendation_content_2 = :recommendation_content_2,
        recommendation_title_3 = :recommendation_title_3,
        recommendation_content_3 = :recommendation_content_3
    where
        report_id = :report_id
    """

    cursor = conn.cursor()
    try:
        cursor.execute(qry, report.model_dump())
        conn.commit()
        return get_report(report_id=report.report_id)
    finally:
        cursor.close()


def delete_report(report_id: str) -> Report:

    report: Report = get_report(report_id=report_id)

    qry = """
    delete from
        reports
    where
        report_id = :report_id
    """

    cursor = conn.cursor()
    try:
        cursor.execute(qry, {"report_id":report_id})
        conn.commit()
        return report
    finally:
        cursor.close()


def publish_report(report_id: str, public: bool) -> Report:

    qry = """
    update
        reports
    set
        public = :public
    where
        report_id = :report_id
    """
    params = {
            "report_id":report_id,
            "public":public
            }

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        return get_report(report_id=report_id)
    finally:
        cursor.close()
