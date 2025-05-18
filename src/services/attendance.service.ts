async getStudentAttendance(studentId: string, startDate: Date, endDate: Date): Promise<Attendance[]> {
  try {
    const attendanceRecords = await prisma.attendance.findMany({
      where: {
        studentId,
        date: {
          gte: startDate,
          lte: endDate,
        },
      },
      include: {
        student: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            grade: true,
          },
        },
      },
      orderBy: {
        date: 'desc',
      },
    });

    return attendanceRecords;
  } catch (error) {
    console.error('Error fetching student attendance:', error);
    throw new Error('Failed to fetch student attendance records');
  }
} 