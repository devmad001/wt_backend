from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from job_cache_model import Base, JobCacheModel  # Replace 'your_model_file' with your actual file name


class DbStorage:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def create(self, job_id, name, data):
        new_job_cache = JobCacheModel(name=name, job_id=job_id, data=data)
        with self.session() as db:
            db.add(new_job_cache)
            db.commit()
        return new_job_cache

    def find(self, job_id, name):
        with self.session() as db:
            job_cache = db.query(JobCacheModel).filter(JobCacheModel.job_id == job_id, JobCacheModel.name == name).first()
        return job_cache

    def get_data(self, job_id, name):
        job_cache = self.find(job_id, name)
        if job_cache is None:
            return None
        return job_cache.data

    def set_data(self, job_id, name, data):
        with self.session() as db:
            query = db.query(JobCacheModel).filter(JobCacheModel.job_id == job_id, JobCacheModel.name == name)
            if query.count() == 0:
                self.create(job_id, name, data)
                result = 1
            else:
                result = query.update(data)
                self.session().commit()
        return result > 0  # True if any rows were updated

    def delete(self, job_id, name):
        with self.session() as db:
            result = db.query(JobCacheModel).filter(JobCacheModel.job_id == job_id, JobCacheModel.name == name).delete()
            db.commit()
        return result > 0  # True if any rows were deleted
