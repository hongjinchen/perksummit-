from flask import render_template, redirect, url_for, flash, request, jsonify, make_response, send_file, Response
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import app, db
from app.models import User, Course, CourseSchedule, Enrollment

from openpyxl import Workbook
from io import BytesIO
import jwt
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

import logging
import base64
import json


@app.after_request
def add_cors_headers(response):
    allowed_origins = ['https://139.155.144.136', 'https://perksummit.club', 'http://localhost:3000']
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, 'YOUR_SECRET_KEY', algorithms=["HS256"])
            # 这里可以获取 token 中的用户信息，并检查用户权限等
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated

# user part


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            password = data['password']
            email = data['email']
        except (TypeError, KeyError) as e:
            return jsonify(message=f'Malformed request data: {str(e)}', status='error')

        # Check if email already exists in the database
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify(message='Email already in use. Please use a different email.', status='error')

        hashed_password = generate_password_hash(password)
        new_user = User(
                        password=hashed_password, email=email)
        with db.session.begin():
            db.session.add(new_user)
            # db.session.commit()
            new_user_id = new_user.id

        # 生成令牌
        token = jwt.encode(
            {"user_id": new_user_id, "exp": datetime.utcnow() + timedelta(hours=1)},
            app.config["SECRET_KEY"],
        )
        resp = make_response(jsonify(
            {"message": 'Registration successful, please log in.', "status": 'success', "user_id": new_user_id}))
        resp.set_cookie("token", token, max_age=60 * 60,
                        secure=True, httponly=False, samesite="Strict")

        return resp


@app.route('/login', methods=['POST'])
def login():

    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if user is not None and check_password_hash(user.password, password):
            login_user(user)

            # 生成令牌
            token = jwt.encode(
                {"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=1)},
                app.config["SECRET_KEY"],
            )

            # 在这里添加用户的is_admin状态到返回的JSON数据中
            resp = make_response(jsonify(message='Login successful.', status='success',
                                         user_id=user.id, token=token, is_admin=user.is_admin))

            # 设置令牌 cookie
            resp.set_cookie("token", token, max_age=60 * 60,
                            secure=True, httponly=False, samesite="Strict")

            return resp

        return jsonify(message='Login failed.', status='failed')


@app.route('/courses', methods=['GET'])
def get_courses():
    courses = db.session.query(Course).options(
        joinedload(Course.schedules)).all()
    result = []
    for course in courses:
        course_data = {
            'id': course.id,
            'name': course.name,
            'lecturer_name': course.lecturer_name,
            'enrollment_limit': course.enrollment_limit,
            'description': course.description,
            'course_type': course.course_type,
            'times': [
                {
                    'id': schedule.id,
                    'time': schedule.time,
                    'registered': schedule.registered,
                    'max': schedule.max
                }
                for schedule in course.schedules
            ],
            'registered': len(course.enrollments)
        }
        result.append(course_data)

    return jsonify(result)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email
    })


@app.route('/changePassword/<int:user_id>', methods=['PUT'])
def change_password(user_id):
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    data = request.get_json()

    user = User.query.get(user_id)

    if user is None:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if "old_password" not in data or "new_password" not in data:
        return jsonify({"status": "error", "message": "Missing old_password or new_password in request"}), 400

    if not check_password_hash(user.password,  data["old_password"]):
        return jsonify({"status": "error", "message": "Incorrect old password"}), 403
    hashed_password = generate_password_hash(data["new_password"])
    user.password = hashed_password
    db.session.commit()

    return jsonify({"status": "success", "message": "Password changed successfully"}), 200

@app.route('/courseSelection', methods=['POST'])
def course_selection():
    try:
        #         # 获取当前时间
        # current_time = datetime.now()
        
        # # 定义时间限制
        # allowed_time1_start = datetime(2023, 8, 3, 16, 0)
        # allowed_time1_end = datetime(2023, 8, 3, 23, 59)
        # allowed_time2_start = datetime(2023, 8, 4, 10, 0)
        # allowed_time2_end = datetime(2023, 8, 5, 10, 0)

        # # 检查当前时间是否在允许的时间范围内
        # if not ((allowed_time1_start <= current_time <= allowed_time1_end) or (allowed_time2_start <= current_time <= allowed_time2_end)):
        #     return jsonify({"error": "This endpoint can only be used at specific times"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user = User.query.get(data.get('userId'))
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 获取用户当前已注册的所有课程及其时间段
        current_enrollments = {(enrollment.course_id, enrollment.course_time)
                               for enrollment in Enrollment.query.filter_by(user_id=user.id).all()}

        new_courses_data = data.get('courses', [])

        # 找出需要删除的课程时间段
        courses_to_delete = current_enrollments - {(course_data['course_id'], course_data['course_time']) for course_data in new_courses_data}
        
        # 删除不再需要的课程时间段
        for course_id, course_time in courses_to_delete:
            schedule_to_decrease = CourseSchedule.query.filter_by(
                course_id=course_id, time=course_time).first()

            # 如果找到了相应的时间段，并且注册人数大于0，则减少注册人数
            if schedule_to_decrease and schedule_to_decrease.registered > 0:
                schedule_to_decrease.registered -= 1

            Enrollment.query.filter_by(
                user_id=user.id, course_id=course_id, course_time=course_time).delete()

        for course_data in new_courses_data:
            course_id = course_data.get('course_id')
            course_time = course_data.get('course_time')

            # 如果已经注册过这个时间段，跳过
            if (course_id, course_time) in current_enrollments:
                continue

            # 在这里找到相应的时间段
            schedule = CourseSchedule.query.filter_by(
                course_id=course_id, time=course_time).first()
            
            if not schedule:
                return jsonify({"error": f"No schedule found for course with id {course_id}"}), 400

            if schedule.registered >= schedule.max:
                return jsonify({"error": f"Course with id {course_id} has been fully booked"}), 400

            # 更新已注册人数
            schedule.registered += 1

            enrollment = Enrollment(
                user_id=user.id, course_id=course_id, course_time=course_time)
            db.session.add(enrollment)

            app.logger.info(
                f'Updated registered count for schedule {schedule.id}. New count: {schedule.registered}')

        db.session.commit()

    except Exception as e:
        app.logger.error(
            f'An error occurred during course registration: {str(e)}')
        return jsonify({"error": "An unexpected error occurred"}), 500

    return jsonify({"message": "Courses registered successfully"}), 200

# @app.route('/courseSelection', methods=['POST'])
# def course_selection():
#     try:
#         data = request.get_json()
#         print(data)
#         if not data:
#             return jsonify({"error": "No data provided"}), 400

#         user = User.query.get(data.get('userId'))
#         if not user:
#             return jsonify({"error": "User not found"}), 404

#         # 获取用户当前已注册的所有课程
#         current_enrollments = Enrollment.query.filter_by(user_id=user.id).all()
#         current_courses_ids = {
#             enrollment.course_id for enrollment in current_enrollments}

#         new_courses_data = data.get('courses', [])
#         new_courses_ids = {course_data.get(
#             'course_id') for course_data in new_courses_data}

#         # 找出需要删除的课程
#         courses_to_delete = current_courses_ids - new_courses_ids

#         # 删除不再需要的课程
#         for course_id in courses_to_delete:
#             Enrollment.query.filter_by(
#                 user_id=user.id, course_id=course_id).delete()

#         for course_data in new_courses_data:
#             course_id = course_data.get('course_id')
#             course = Course.query.get(course_id)
#             if not course:
#                 return jsonify({"error": f"Course with id {course_id} not found"}), 404

#             # 如果已经注册过，跳过
#             if course.id in current_courses_ids:
#                 continue

#             if course.enrollment_limit <= len(course.enrollments):
#                 return jsonify({"error": f"Course {course.name} is full"}), 400

#             # 在这里找到相应的时间段并更新它的已注册人数
#             course_time = course_data.get('course_time')
#             schedule = CourseSchedule.query.filter_by(
#                 course_id=course_id, time=course_time).first()

#             if schedule is not None:
#                 if schedule.registered >= schedule.max:
#                     return jsonify({"error": f"Course with id {course_id} has been fully booked"}), 400
#                 schedule.registered += 1
#             else:
#                 return jsonify({"error": f"No schedule found for course with id {course_id}"}), 400

#             enrollment = Enrollment(
#                 user_id=user.id, course_id=course.id, course_time=course_data.get('course_time'))
#             db.session.add(enrollment)

#             app.logger.info(
#                 f'Updated registered count for schedule {schedule.id}. New count: {schedule.registered}')

#         db.session.commit()

#     except Exception as e:
#         app.logger.error(
#             f'An error occurred during course registration: {str(e)}')
#         return jsonify({"error": "An unexpected error occurred"}), 500

#     return jsonify({"message": "Courses registered successfully"}), 200


# @app.route('/selectedCourses/<userId>', methods=['GET'])
# def get_selected_courses(userId):
#     user = User.query.get(userId)

#     if not user:
#         app.logger.error(f'User {userId} not found')
#         return jsonify({"error": "User not found"}), 404

#     # 获取用户的已选课程
#     enrolled_courses = []
#     for enrollment in user.enrollments:
#         course = Course.query.options(joinedload(
#             Course.schedules)).get(enrollment.course_id)
#         if course:
#             selected_time = next(
#                 (time for time in course.schedules if time.time == enrollment.course_time), None)
#             if not selected_time:
#                 app.logger.error(
#                     f'Enrollment time {enrollment.course_time} not found in course {course.id} schedules')
#                 return jsonify({"error": "Enrollment time not found"}), 404

#             selected_time_data = {
#                 'id': selected_time.id,
#                 'time': selected_time.time,
#                 'registered': selected_time.registered,
#                 'max': selected_time.max
#             }
#             course_data = {
#                 'id': course.id,
#                 'name': course.name,
#                 'lecturer_name': course.lecturer_name,
#                 'enrollment_limit': course.enrollment_limit,
#                 'description': course.description,
#                 'course_type': course.course_type,
#                 'times': [
#                     {
#                         'id': schedule.id,
#                         'time': schedule.time,
#                         'registered': schedule.registered,
#                         'max': schedule.max
#                     }
#                     for schedule in course.schedules
#                 ],
#                 'selectedTime': selected_time_data,
#                 'registered': len(course.enrollments)
#             }
#             enrolled_courses.append(course_data)

#     return jsonify(enrolled_courses), 200


@app.route('/selectedCourses/<userId>', methods=['GET'])
def get_selected_courses(userId):
    user = User.query.get(userId)

    if not user:
        app.logger.error(f'User {userId} not found')
        return jsonify({"error": "User not found"}), 404

    # 获取用户的已选课程
    enrolled_courses = []
    for enrollment in user.enrollments:
        course = Course.query.options(joinedload(
            Course.schedules)).get(enrollment.course_id)
        if course:
            selected_time = next(
                (time for time in course.schedules if time.time == enrollment.course_time), None)
            if not selected_time:
                app.logger.error(
                    f'Enrollment time {enrollment.course_time} not found in course {course.id} schedules')
                return jsonify({"error": "Enrollment time not found"}), 404

            selected_time_data = {
                'id': selected_time.id,
                'time': selected_time.time,
                'registered': selected_time.registered,
                'max': selected_time.max
            }
            # 检查是否已经添加了相同的课程
            existing_course = next((c for c in enrolled_courses if c['id'] == course.id), None)
            if existing_course:
                existing_course['selectedTime'].append(selected_time_data)
            else:
                course_data = {
                    'id': course.id,
                    'name': course.name,
                    'lecturer_name': course.lecturer_name,
                    'enrollment_limit': course.enrollment_limit,
                    'description': course.description,
                    'course_type': course.course_type,
                    'times': [
                        {
                            'id': schedule.id,
                            'time': schedule.time,
                            'registered': schedule.registered,
                            'max': schedule.max
                        }
                        for schedule in course.schedules
                    ],
                    'selectedTime': [selected_time_data], # 确保是一个数组
                    'registered': len(course.enrollments)
                }
                enrolled_courses.append(course_data)

    return jsonify(enrolled_courses), 200

@app.route('/api/courses', methods=['GET'])
def get_courses_admin():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])


@app.route('/api/export-courses', methods=['GET'])
def export_courses():
    courses = Course.query.all()

    wb = Workbook()
    ws = wb.active

    ws.append(['课程名', '讲师名字', '课程时间', '注册人数', '注册名单'])

    for course in courses:
        for schedule in course.schedules:
            enrollments_for_schedule = [enrollment for enrollment in course.enrollments if enrollment.course_time == schedule.time]
            enrollment_users = ', '.join([enrollment.user.email for enrollment in enrollments_for_schedule])
            ws.append([course.name, course.lecturer_name, schedule.time, schedule.registered, enrollment_users])

    mem = BytesIO()
    wb.save(mem)
    mem.seek(0)

    response = Response(
        mem, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers.set('Content-Disposition',
                         'attachment', filename='courses.xlsx')

    return response



@app.route('/resetpassword', methods=['POST'])
def reset_password():
    email = request.json.get('email')
    new_password = request.json.get('password')

    # 在数据库中查找匹配的用户
    try:
        user = User.query.filter_by(email=email).one()
    except NoResultFound:
        return jsonify({'status': 'error', 'message': '没有找到匹配的用户'}), 404

    # 更新用户的密码
    hashed_password = generate_password_hash(new_password)
    user.password = hashed_password
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/api/users', methods=['GET'])
def get_users():
    print("Getting users")
    users = User.query.filter(User.email != 'admin').all()
    user_data = [{'email': user.email, 'id': user.id} for user in users]
    return jsonify({'status': 'success', 'users': user_data})


@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user is not None:
        # First, delete all enrollments of the user
        Enrollment.query.filter_by(user_id=id).delete()
        # Then, delete the user
        db.session.delete(user)
        db.session.commit()

    return jsonify({'status': 'success'}), 200