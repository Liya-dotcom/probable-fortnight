# main.py
import os
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date  # Add 'date' to the imports
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("localhost"),
            user=os.getenv("root"),
            password=os.getenv("Liya@0307"),
            database=os.getenv("task_magaer")
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

# Models
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    created_by: int

class Project(ProjectBase):
    project_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    due_date: Optional[date] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None

class TaskCreate(TaskBase):
    created_by: int

class Task(TaskBase):
    task_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: int
    user_id: int

class Comment(CommentBase):
    comment_id: int
    task_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Users CRUD (same as before)
@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (user.username, user.email, user.password))
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        new_user = cursor.fetchone()
        return new_user
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = "SELECT user_id, username, email, created_at FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        connection.close()

# Projects CRUD
@app.post("/projects/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (project.created_by,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        query = """
        INSERT INTO projects (name, description, created_by)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            project.name, project.description, project.created_by
        ))
        connection.commit()
        
        project_id = cursor.lastrowid
        cursor.execute("SELECT * FROM projects WHERE project_id = %s", (project_id,))
        new_project = cursor.fetchone()
        return new_project
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating project: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM projects WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        project = cursor.fetchone()
        
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    finally:
        cursor.close()
        connection.close()

# Tasks CRUD
@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if creator exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (task.created_by,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Creator user not found")
        
        # Check if assigned user exists (if provided)
        if task.assigned_to:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (task.assigned_to,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Assigned user not found")
        
        # Check if project exists (if provided)
        if task.project_id:
            cursor.execute("SELECT project_id FROM projects WHERE project_id = %s", (task.project_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Project not found")
        
        query = """
        INSERT INTO tasks (
            title, description, status, priority, due_date, 
            project_id, assigned_to, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            task.title, task.description, task.status, task.priority,
            task.due_date, task.project_id, task.assigned_to, task.created_by
        ))
        connection.commit()
        
        task_id = cursor.lastrowid
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        new_task = cursor.fetchone()
        return new_task
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating task: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM tasks WHERE task_id = %s"
        cursor.execute(query, (task_id,))
        task = cursor.fetchone()
        
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    finally:
        cursor.close()
        connection.close()

@app.get("/projects/{project_id}/tasks", response_model=List[Task])
def read_project_tasks(project_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if project exists
        cursor.execute("SELECT project_id FROM projects WHERE project_id = %s", (project_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Project not found")
        
        query = "SELECT * FROM tasks WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        tasks = cursor.fetchall()
        return tasks
    finally:
        cursor.close()
        connection.close()

# Comments CRUD
@app.post("/comments/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if task exists
        cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s", (comment.task_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (comment.user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        
        query = """
        INSERT INTO comments (content, task_id, user_id)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            comment.content, comment.task_id, comment.user_id
        ))
        connection.commit()
        
        comment_id = cursor.lastrowid
        cursor.execute("SELECT * FROM comments WHERE comment_id = %s", (comment_id,))
        new_comment = cursor.fetchone()
        return new_comment
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating comment: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.get("/tasks/{task_id}/comments", response_model=List[Comment])
def read_task_comments(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if task exists
        cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s", (task_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Task not found")
        
        query = "SELECT * FROM comments WHERE task_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (task_id,))
        comments = cursor.fetchall()
        return comments
    finally:
        cursor.close()
        connection.close()

# Update and Delete endpoints for all models would follow similar patterns
# Implemented for tasks as an example

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskBase):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if task exists
        cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s", (task_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if assigned user exists (if provided)
        if task.assigned_to:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (task.assigned_to,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Assigned user not found")
        
        # Check if project exists (if provided)
        if task.project_id:
            cursor.execute("SELECT project_id FROM projects WHERE project_id = %s", (task.project_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Project not found")
        
        query = """
        UPDATE tasks 
        SET title = %s, description = %s, status = %s, priority = %s, 
            due_date = %s, project_id = %s, assigned_to = %s
        WHERE task_id = %s
        """
        cursor.execute(query, (
            task.title, task.description, task.status, task.priority,
            task.due_date, task.project_id, task.assigned_to, task_id
        ))
        connection.commit()
        
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        updated_task = cursor.fetchone()
        return updated_task
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating task: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Check if task exists
        cursor.execute("SELECT task_id FROM tasks WHERE task_id = %s", (task_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete task (comments will be deleted automatically due to CASCADE)
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        connection.commit()
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting task: {e}"
        )
    finally:
        cursor.close()
        connection.close()