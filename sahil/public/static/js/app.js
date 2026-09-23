/**
 * Serverless Student Result Management System - Frontend App Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // State
  let allStudents = [];
  let currentFilter = 'all';
  let currentSemesterFilter = 'all';
  let activeStudentRoll = null;

  // DOM Elements
  const tableBody = document.getElementById('table-body');
  const searchInput = document.getElementById('search-input');
  const searchClearBtn = document.getElementById('search-clear-btn');
  const filterPills = document.querySelectorAll('.filter-pill');
  const filterSemester = document.getElementById('filter-semester');
  const btnRefresh = document.getElementById('btn-refresh-data');
  const btnSeed = document.getElementById('btn-seed-data');

  // Stats DOM
  const valTotalStudents = document.getElementById('val-total-students');
  const valPassRate = document.getElementById('val-pass-rate');
  const valPassCount = document.getElementById('val-pass-count');
  const valClassAvg = document.getElementById('val-class-avg');
  const valTopPerformer = document.getElementById('val-top-performer');
  const valTopScore = document.getElementById('val-top-score');

  // Modals
  const modalResult = document.getElementById('modal-result-card');
  const modalRegister = document.getElementById('modal-register-student');
  const modalEdit = document.getElementById('modal-edit-student');
  const modalMarks = document.getElementById('modal-add-marks');
  const resultCardBody = document.getElementById('result-card-body');

  // Buttons for Modals
  const btnOpenRegister = document.getElementById('btn-open-register-modal');
  const btnCloseRegister = document.getElementById('btn-close-register-modal');
  const btnCancelRegister = document.getElementById('btn-cancel-register');
  const btnCloseEdit = document.getElementById('btn-close-edit-modal');
  const btnCancelEdit = document.getElementById('btn-cancel-edit');
  const btnCloseResult = document.getElementById('btn-close-result-modal');
  const btnCloseMarks = document.getElementById('btn-close-marks-modal');
  const btnCancelMarks = document.getElementById('btn-cancel-marks');
  const btnResultAddMore = document.getElementById('btn-result-add-more-marks');

  // Forms
  const formRegister = document.getElementById('form-register-student');
  const formEdit = document.getElementById('form-edit-student');
  const formMarks = document.getElementById('form-add-marks');
  const marksRollInput = document.getElementById('marks-roll');
  const marksObtainedInput = document.getElementById('marks-obtained');
  const marksMaxInput = document.getElementById('marks-max');
  const previewPct = document.getElementById('preview-pct');
  const previewStatus = document.getElementById('preview-status');
  const marksModalStudentName = document.getElementById('marks-modal-student-name');

  // Edit form inputs
  const editRollInput = document.getElementById('edit-roll');
  const editNameInput = document.getElementById('edit-name');
  const editEmailInput = document.getElementById('edit-email');
  const editCourseInput = document.getElementById('edit-course');
  const editSemSelect = document.getElementById('edit-sem');

  // =========================================================================
  // Toast Notifications
  // =========================================================================
  function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // =========================================================================
  // Fetch & Render Dashboard Data
  // =========================================================================
  async function loadDashboardData() {
    try {
      tableBody.innerHTML = `
        <tr>
          <td colspan="9" class="empty-state">
            <div class="spinner"></div>
            <p>Syncing records from database...</p>
          </td>
        </tr>
      `;

      const response = await fetch('/api/summary');
      if (!response.ok) {
        let errMsg = `HTTP ${response.status}`;
        try {
          const errData = await response.json();
          if (errData && errData.error) errMsg = errData.error;
        } catch (_) {}
        throw new Error(errMsg);
      }

      const summaryRes = await response.json();

      if (summaryRes.success) {
        allStudents = summaryRes.data || [];
        updateStats(allStudents);
        renderTable(allStudents);
      } else {
        tableBody.innerHTML = `<tr><td colspan="9" class="empty-state">${escapeHtml(summaryRes.error || 'Failed to load student data.')}</td></tr>`;
        showToast(summaryRes.error || 'Database error loading records', 'error');
      }
    } catch (err) {
      console.error('Data load error:', err);
      tableBody.innerHTML = `
        <tr>
          <td colspan="9" class="empty-state">
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 28px; margin-bottom: 8px; color: var(--danger); display: block;"></i>
            <p>Unable to connect to backend database.</p>
            <p style="font-size: 0.85rem; color: var(--text-dim); margin: 6px 0 12px;">${escapeHtml(err.message || 'Server connection failed')}</p>
            <button class="btn btn-secondary" onclick="loadDashboardData()" style="display: inline-flex; align-items: center; gap: 6px; margin: 0 auto;">
              <i class="fa-solid fa-rotate"></i> Retry Connection
            </button>
          </td>
        </tr>
      `;
      showToast('Error connecting to backend database: ' + (err.message || 'Server unreachable'), 'error');
    }
  }

  // Update Top Stats Cards
  function updateStats(students) {
    valTotalStudents.textContent = students.length;

    if (students.length === 0) {
      valPassRate.textContent = '0%';
      valPassCount.textContent = '0 passed';
      valClassAvg.textContent = '0%';
      valTopPerformer.textContent = 'N/A';
      valTopScore.textContent = '0%';
      return;
    }

    const passedList = students.filter(s => s.status === 'PASS');
    const passPct = ((passedList.length / students.length) * 100).toFixed(1);
    valPassRate.textContent = `${passPct}%`;
    valPassCount.textContent = `${passedList.length} of ${students.length} passed`;

    const totalScores = students.reduce((acc, s) => acc + (s.percentage || 0), 0);
    valClassAvg.textContent = `${(totalScores / students.length).toFixed(1)}%`;

    // Find top performer
    const sorted = [...students].sort((a, b) => (b.percentage || 0) - (a.percentage || 0));
    if (sorted.length > 0 && sorted[0].percentage > 0) {
      valTopPerformer.textContent = sorted[0].name;
      valTopScore.textContent = `${sorted[0].percentage.toFixed(1)}% (${sorted[0].roll_no})`;
    } else {
      valTopPerformer.textContent = 'None yet';
      valTopScore.textContent = '0%';
    }
  }

  // Render Table Rows
  function renderTable(students) {
    // Filter by Pass/Fail status
    let filtered = students;
    if (currentFilter !== 'all') {
      filtered = filtered.filter(s => s.status === currentFilter);
    }

    // Filter by Semester
    if (currentSemesterFilter !== 'all') {
      filtered = filtered.filter(s => String(s.semester) === String(currentSemesterFilter));
    }

    // Filter by search query
    const query = searchInput.value.trim().toLowerCase();
    if (query) {
      filtered = filtered.filter(s => 
        (s.roll_no && s.roll_no.toLowerCase().includes(query)) ||
        (s.name && s.name.toLowerCase().includes(query)) ||
        (s.course && s.course.toLowerCase().includes(query)) ||
        (`sem ${s.semester}`.includes(query)) ||
        (`semester ${s.semester}`.includes(query))
      );
    }

    if (filtered.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="9" class="empty-state">
            <i class="fa-solid fa-folder-open" style="font-size: 28px; margin-bottom: 8px; color: var(--text-dim); display: block;"></i>
            No student records found matching the selected semester and filters.
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = filtered.map(s => {
      const initials = s.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
      const pct = s.percentage !== undefined ? s.percentage : 0;
      const isPass = s.status === 'PASS';
      const isFail = s.status === 'FAIL';
      const progressClass = isPass ? 'pass' : (isFail ? 'fail' : '');

      let statusBadge = `<span class="status-pill neutral">NO MARKS</span>`;
      if (isPass) statusBadge = `<span class="status-pill pass"><i class="fa-solid fa-check"></i> PASS</span>`;
      if (isFail) statusBadge = `<span class="status-pill fail"><i class="fa-solid fa-xmark"></i> FAIL</span>`;

      const gradeKey = s.grade === 'A+' ? 'Aplus' : (s.grade === 'B+' ? 'Bplus' : (s.grade || 'NA'));

      return `
        <tr>
          <td><span class="roll-badge">${s.roll_no}</span></td>
          <td>
            <div class="student-info-cell">
              <div class="student-avatar">${initials}</div>
              <div>
                <div class="student-name-text">${escapeHtml(s.name)}</div>
                <div class="student-email-text">${s.roll_no}</div>
              </div>
            </div>
          </td>
          <td>
            <div style="font-weight: 500; color: #e2e8f0;">${escapeHtml(s.course)}</div>
          </td>
          <td>
            <span class="sem-badge">
              <i class="fa-solid fa-layer-group"></i> Semester ${s.semester || 1}
            </span>
          </td>
          <td>
            <strong>${s.total_obtained || 0}</strong>
            <span style="color: var(--text-dim); font-size: 0.8rem;"> / ${s.total_max || 0}</span>
          </td>
          <td>
            <div class="pct-cell">
              <div class="progress-track">
                <div class="progress-fill ${progressClass}" style="width: ${Math.min(pct, 100)}%;"></div>
              </div>
              <span style="font-weight: 600;">${pct.toFixed(1)}%</span>
            </div>
          </td>
          <td>
            <span class="grade-badge grade-${gradeKey}">${s.grade || 'N/A'}</span>
          </td>
          <td>${statusBadge}</td>
          <td class="text-right">
            <div class="action-cell">
              <button class="btn-table-action" onclick="viewResultCard('${s.roll_no}')" title="View Result Transcript">
                <i class="fa-solid fa-file-lines"></i>
              </button>
              <button class="btn-table-action" onclick="openMarksModal('${s.roll_no}', '${escapeHtml(s.name)}')" title="Add or Update Marks">
                <i class="fa-solid fa-pen"></i>
              </button>
              <button class="btn-table-action" onclick="openEditStudentModal('${s.roll_no}')" title="Edit Student & Semester">
                <i class="fa-solid fa-user-pen"></i>
              </button>
              <button class="btn-table-action danger" onclick="deleteStudentRecord('${s.roll_no}')" title="Delete Student">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
  }

  // =========================================================================
  // Search & Filter Events
  // =========================================================================
  searchInput.addEventListener('input', () => {
    searchClearBtn.style.display = searchInput.value ? 'block' : 'none';
    renderTable(allStudents);
  });

  searchClearBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchClearBtn.style.display = 'none';
    renderTable(allStudents);
  });

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentFilter = pill.getAttribute('data-filter');
      renderTable(allStudents);
    });
  });

  if (filterSemester) {
    filterSemester.addEventListener('change', (e) => {
      currentSemesterFilter = e.target.value;
      renderTable(allStudents);
    });
  }

  btnRefresh.addEventListener('click', () => {
    loadDashboardData();
    showToast('Database refreshed.');
  });

  // Seed Data
  btnSeed.addEventListener('click', async () => {
    try {
      btnSeed.disabled = true;
      btnSeed.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Seeding...`;
      const res = await fetch('/api/seed', { method: 'POST' }).then(r => r.json());
      if (res.success) {
        showToast('Sample students and marks loaded!');
        await loadDashboardData();
      } else {
        showToast(res.error || 'Failed to seed sample data', 'error');
      }
    } catch (e) {
      showToast('Error executing seed request', 'error');
    } finally {
      btnSeed.disabled = false;
      btnSeed.innerHTML = `<i class="fa-solid fa-database"></i> <span>Seed Sample Data</span>`;
    }
  });

  // =========================================================================
  // Result Card Modal
  // =========================================================================
  window.viewResultCard = async function(rollNo) {
    activeStudentRoll = rollNo;
    modalResult.style.display = 'flex';
    resultCardBody.innerHTML = `
      <div class="empty-state">
        <div class="spinner"></div>
        <p>Generating academic transcript...</p>
      </div>
    `;

    try {
      const res = await fetch(`/api/results/${rollNo}`).then(r => r.json());
      if (!res.success) {
        resultCardBody.innerHTML = `<div class="empty-state"><p>${res.error || 'Failed to retrieve result.'}</p></div>`;
        return;
      }

      const { student, subjects, summary } = res.data;
      const isPass = summary.status === 'PASS';
      const statusColor = isPass ? '#10b981' : '#f43f5e';

      resultCardBody.innerHTML = `
        <div class="transcript-card">
          <div class="transcript-meta-grid">
            <div class="meta-field"><span>Student Name</span><strong>${escapeHtml(student.name)}</strong></div>
            <div class="meta-field"><span>Roll Number</span><strong>${student.roll_no}</strong></div>
            <div class="meta-field"><span>Course</span><strong>${escapeHtml(student.course)}</strong></div>
            <div class="meta-field"><span>Academic Semester</span><strong style="color: #a5b4fc;">Semester ${student.semester}</strong></div>
            <div class="meta-field" style="grid-column: span 2;"><span>Registered Email</span><strong>${escapeHtml(student.email)}</strong></div>
          </div>

          <table class="transcript-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Subject Name</th>
                <th>Marks</th>
                <th>Max</th>
                <th>%</th>
                <th>Status</th>
                <th class="text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              ${subjects.length === 0 ? `
                <tr><td colspan="7" class="empty-state" style="padding: 20px !important;">No subjects recorded yet for this student.</td></tr>
              ` : subjects.map((sub, idx) => `
                <tr>
                  <td>${idx + 1}</td>
                  <td><strong>${escapeHtml(sub.subject_name)}</strong></td>
                  <td>${sub.marks_obtained}</td>
                  <td>${sub.max_marks}</td>
                  <td>${sub.percentage}%</td>
                  <td>
                    <span class="status-pill ${sub.status === 'PASS' ? 'pass' : 'fail'}">
                      ${sub.status}
                    </span>
                  </td>
                  <td class="text-right">
                    <button class="btn-table-action danger" onclick="deleteSubjectMarks('${student.roll_no}', '${encodeURIComponent(sub.subject_name)}')" title="Delete Subject">
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div class="transcript-summary-box">
            <div class="summary-stat-block">
              <span>Total Score</span>
              <h4>${summary.total_marks_obtained} / ${summary.total_max_marks}</h4>
            </div>
            <div class="summary-stat-block">
              <span>Aggregate %</span>
              <h4>${summary.percentage.toFixed(2)}%</h4>
            </div>
            <div class="summary-stat-block">
              <span>Letter Grade</span>
              <h4 style="color: #818cf8;">${summary.grade}</h4>
            </div>
            <div class="summary-stat-block">
              <span>Final Evaluation</span>
              <h4 style="color: ${statusColor};">${summary.status}</h4>
            </div>
          </div>

          ${summary.failed_subjects_count > 0 ? `
            <div style="margin-top: 14px; padding: 10px; background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 8px; font-size: 0.82rem; color: #fb7185;">
              <i class="fa-solid fa-circle-exclamation"></i> Notice: Candidate has not met passing threshold in ${summary.failed_subjects_count} subject(s).
            </div>
          ` : ''}
        </div>
      `;
    } catch (e) {
      resultCardBody.innerHTML = `<div class="empty-state">Error generating card.</div>`;
    }
  };

  btnCloseResult.addEventListener('click', () => modalResult.style.display = 'none');
  btnResultAddMore.addEventListener('click', () => {
    modalResult.style.display = 'none';
    if (activeStudentRoll) {
      const stu = allStudents.find(s => s.roll_no === activeStudentRoll);
      openMarksModal(activeStudentRoll, stu ? stu.name : activeStudentRoll);
    }
  });

  // Delete subject marks
  window.deleteSubjectMarks = async function(rollNo, encodedSubj) {
    if (!confirm('Are you sure you want to delete this subject mark?')) return;
    try {
      const res = await fetch(`/api/results/${rollNo}/${encodedSubj}`, { method: 'DELETE' }).then(r => r.json());
      if (res.success) {
        showToast('Subject deleted.');
        viewResultCard(rollNo);
        loadDashboardData();
      } else {
        showToast(res.error || 'Failed to delete subject', 'error');
      }
    } catch (e) {
      showToast('Error deleting subject', 'error');
    }
  };

  // =========================================================================
  // Register Student Modal & Form
  // =========================================================================
  btnOpenRegister.addEventListener('click', () => {
    formRegister.reset();
    modalRegister.style.display = 'flex';
  });

  btnCloseRegister.addEventListener('click', () => modalRegister.style.display = 'none');
  btnCancelRegister.addEventListener('click', () => modalRegister.style.display = 'none');

  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      roll_no: document.getElementById('reg-roll').value.trim(),
      name: document.getElementById('reg-name').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      course: document.getElementById('reg-course').value.trim(),
      semester: parseInt(document.getElementById('reg-sem').value, 10)
    };

    try {
      const res = await fetch('/api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(r => r.json());

      if (res.success) {
        showToast(`Student ${payload.name} registered for Semester ${payload.semester}!`);
        modalRegister.style.display = 'none';
        await loadDashboardData();
      } else {
        showToast(res.error || 'Registration failed', 'error');
      }
    } catch (err) {
      showToast('Error registering student', 'error');
    }
  });

  // =========================================================================
  // Edit Student & Semester Modal
  // =========================================================================
  window.openEditStudentModal = async function(rollNo) {
    try {
      const res = await fetch(`/api/students/${rollNo}`).then(r => r.json());
      if (!res.success) {
        showToast(res.error || 'Student not found', 'error');
        return;
      }
      const s = res.data;
      editRollInput.value = s.roll_no;
      editNameInput.value = s.name;
      editEmailInput.value = s.email;
      editCourseInput.value = s.course;
      editSemSelect.value = String(s.semester || 1);
      modalEdit.style.display = 'flex';
    } catch (err) {
      showToast('Failed to load student details for editing', 'error');
    }
  };

  if (btnCloseEdit) btnCloseEdit.addEventListener('click', () => modalEdit.style.display = 'none');
  if (btnCancelEdit) btnCancelEdit.addEventListener('click', () => modalEdit.style.display = 'none');

  if (formEdit) {
    formEdit.addEventListener('submit', async (e) => {
      e.preventDefault();
      const rollNo = editRollInput.value.trim();
      const payload = {
        name: editNameInput.value.trim(),
        email: editEmailInput.value.trim(),
        course: editCourseInput.value.trim(),
        semester: parseInt(editSemSelect.value, 10)
      };

      try {
        const res = await fetch(`/api/students/${rollNo}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(r => r.json());

        if (res.success) {
          showToast(`Student ${rollNo} updated to Semester ${payload.semester}!`);
          modalEdit.style.display = 'none';
          await loadDashboardData();
        } else {
          showToast(res.error || 'Failed to update student', 'error');
        }
      } catch (err) {
        showToast('Error updating student', 'error');
      }
    });
  }

  // =========================================================================
  // Add / Update Marks Modal & Form (Batch & Multi-Subject)
  // =========================================================================
  const subjectRowsContainer = document.getElementById('subject-rows-container');
  const btnAddSubjectRow = document.getElementById('btn-add-subject-row');
  const btnPresetCs = document.getElementById('btn-preset-cs');
  const btnPresetEce = document.getElementById('btn-preset-ece');
  const btnPresetFirstYear = document.getElementById('btn-preset-firstyear');
  const btnPresetClear = document.getElementById('btn-preset-clear');
  const previewTotalSubjects = document.getElementById('preview-total-subjects');
  const previewCumulativeScore = document.getElementById('preview-cumulative-score');

  function createSubjectRow(subjectName = '', marks = '', maxMarks = 100) {
    const row = document.createElement('div');
    row.className = 'subject-entry-row';
    row.innerHTML = `
      <input type="text" class="form-control batch-subject-name" placeholder="e.g. Operating Systems" value="${escapeHtml(subjectName)}" required style="flex: 2.2;">
      <input type="number" step="0.5" min="0" class="form-control batch-marks-obtained" placeholder="Marks" value="${marks}" required style="flex: 1.1;">
      <input type="number" step="0.5" min="1" class="form-control batch-marks-max" placeholder="Max" value="${maxMarks}" required style="flex: 1.1;">
      <button type="button" class="btn-remove-row" title="Remove Subject"><i class="fa-solid fa-trash-can"></i></button>
    `;

    const nameInp = row.querySelector('.batch-subject-name');
    const marksInp = row.querySelector('.batch-marks-obtained');
    const maxInp = row.querySelector('.batch-marks-max');
    const btnRemove = row.querySelector('.btn-remove-row');

    marksInp.addEventListener('input', updateBatchPreview);
    maxInp.addEventListener('input', updateBatchPreview);
    nameInp.addEventListener('input', updateBatchPreview);

    btnRemove.addEventListener('click', () => {
      row.remove();
      if (subjectRowsContainer.children.length === 0) {
        createSubjectRow();
      }
      updateBatchPreview();
    });

    subjectRowsContainer.appendChild(row);
    return row;
  }

  function updateBatchPreview() {
    const rows = subjectRowsContainer.querySelectorAll('.subject-entry-row');
    let totalObtained = 0;
    let totalMax = 0;
    let validCount = 0;
    let anyFailed = false;

    rows.forEach(r => {
      const name = r.querySelector('.batch-subject-name').value.trim();
      const mStr = r.querySelector('.batch-marks-obtained').value;
      const maxStr = r.querySelector('.batch-marks-max').value;
      if (name && mStr !== '') {
        const m = parseFloat(mStr) || 0;
        const max = parseFloat(maxStr) || 100;
        totalObtained += m;
        totalMax += max;
        validCount++;
        if (max > 0 && (m / max) * 100 < 35) {
          anyFailed = true;
        }
      }
    });

    if (previewTotalSubjects) previewTotalSubjects.textContent = validCount;
    if (previewCumulativeScore) previewCumulativeScore.textContent = `${totalObtained.toFixed(1)} / ${totalMax.toFixed(1)}`;

    if (validCount === 0 || totalMax === 0) {
      if (previewPct) previewPct.textContent = '0.0%';
      if (previewStatus) {
        previewStatus.textContent = 'Awaiting Input';
        previewStatus.className = 'badge-status-neutral';
      }
      return;
    }

    const pct = (totalObtained / totalMax) * 100;
    if (previewPct) previewPct.textContent = `${pct.toFixed(2)}%`;

    let grade = 'F';
    if (pct >= 90) grade = 'A+';
    else if (pct >= 80) grade = 'A';
    else if (pct >= 70) grade = 'B+';
    else if (pct >= 60) grade = 'B';
    else if (pct >= 50) grade = 'C';
    else if (pct >= 40) grade = 'P';

    if (previewStatus) {
      if (!anyFailed && pct >= 40) {
        previewStatus.textContent = `PASS (Grade ${grade})`;
        previewStatus.className = 'status-pill pass';
      } else {
        previewStatus.textContent = anyFailed ? 'FAIL (Subject < 35%)' : 'FAIL (Aggregate < 40%)';
        previewStatus.className = 'status-pill fail';
      }
    }
  }

  function applyPresetSubjects(subjectsArray) {
    subjectRowsContainer.innerHTML = '';
    subjectsArray.forEach(subj => {
      createSubjectRow(subj, '', 100);
    });
    updateBatchPreview();
    const firstInput = subjectRowsContainer.querySelector('.batch-marks-obtained');
    if (firstInput) firstInput.focus();
  }

  if (btnPresetCs) {
    btnPresetCs.addEventListener('click', () => {
      applyPresetSubjects([
        'Data Structures & Algorithms',
        'Database Management Systems',
        'Operating Systems',
        'Computer Networks',
        'Software Engineering'
      ]);
    });
  }

  if (btnPresetEce) {
    btnPresetEce.addEventListener('click', () => {
      applyPresetSubjects([
        'Digital Signal Processing',
        'Microprocessors & Microcontrollers',
        'VLSI Design',
        'Analog Communication',
        'Electromagnetic Fields'
      ]);
    });
  }

  if (btnPresetFirstYear) {
    btnPresetFirstYear.addEventListener('click', () => {
      applyPresetSubjects([
        'Engineering Mathematics',
        'Engineering Physics',
        'Basic Electrical & Electronics',
        'Problem Solving with Python',
        'Professional Communication'
      ]);
    });
  }

  if (btnPresetClear) {
    btnPresetClear.addEventListener('click', () => {
      subjectRowsContainer.innerHTML = '';
      createSubjectRow('', '', 100);
      updateBatchPreview();
    });
  }

  if (btnAddSubjectRow) {
    btnAddSubjectRow.addEventListener('click', () => {
      const row = createSubjectRow('', '', 100);
      row.querySelector('.batch-subject-name').focus();
    });
  }

  window.openMarksModal = async function(rollNo, studentName) {
    marksRollInput.value = rollNo;
    marksModalStudentName.textContent = `Recording for: ${studentName} (${rollNo})`;
    subjectRowsContainer.innerHTML = '';

    // Check if student already has recorded subjects and pre-fill them
    try {
      const res = await fetch(`/api/results/${rollNo}`).then(r => r.json());
      if (res.success && res.data && res.data.subjects && res.data.subjects.length > 0) {
        res.data.subjects.forEach(s => {
          createSubjectRow(s.subject_name, s.marks_obtained, s.max_marks);
        });
      } else {
        // Pre-fill 3 blank rows for quick streamlined entry
        createSubjectRow('', '', 100);
        createSubjectRow('', '', 100);
        createSubjectRow('', '', 100);
      }
    } catch (e) {
      createSubjectRow('', '', 100);
    }

    updateBatchPreview();
    modalMarks.style.display = 'flex';
  };

  btnCloseMarks.addEventListener('click', () => modalMarks.style.display = 'none');
  btnCancelMarks.addEventListener('click', () => modalMarks.style.display = 'none');

  formMarks.addEventListener('submit', async (e) => {
    e.preventDefault();
    const rollNo = marksRollInput.value;
    const rows = subjectRowsContainer.querySelectorAll('.subject-entry-row');
    const subjectsList = [];

    rows.forEach(r => {
      const subjName = r.querySelector('.batch-subject-name').value.trim();
      const mStr = r.querySelector('.batch-marks-obtained').value.trim();
      const maxStr = r.querySelector('.batch-marks-max').value.trim();
      if (subjName) {
        subjectsList.push({
          subject_name: subjName,
          marks_obtained: parseFloat(mStr) || 0,
          max_marks: parseFloat(maxStr) || 100
        });
      }
    });

    if (subjectsList.length === 0) {
      showToast('Please enter at least one subject with valid marks', 'error');
      return;
    }

    try {
      const submitBtn = document.getElementById('btn-submit-marks');
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Saving...`;

      const res = await fetch(`/api/results/${rollNo}/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subjects: subjectsList })
      }).then(r => r.json());

      if (res.success) {
        showToast(res.message || `Successfully recorded ${subjectsList.length} subjects!`);
        modalMarks.style.display = 'none';
        await loadDashboardData();
        // If result transcript modal was open, refresh it
        if (modalResult.style.display === 'flex') {
          viewResultCard(rollNo);
        }
      } else {
        showToast(res.error || 'Failed to save marks', 'error');
      }
    } catch (err) {
      showToast('Error connecting to server to save marks', 'error');
    } finally {
      const submitBtn = document.getElementById('btn-submit-marks');
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> Save All Subjects`;
    }
  });

  // Delete Student
  window.deleteStudentRecord = async function(rollNo) {
    if (!confirm(`Are you sure you want to permanently delete student ${rollNo} and all related marks?`)) {
      return;
    }
    try {
      const res = await fetch(`/api/students/${rollNo}`, { method: 'DELETE' }).then(r => r.json());
      if (res.success) {
        showToast(`Student ${rollNo} deleted.`);
        await loadDashboardData();
      } else {
        showToast(res.error || 'Failed to delete student', 'error');
      }
    } catch (err) {
      showToast('Error deleting student', 'error');
    }
  };

  // Close modals on outside click
  window.addEventListener('click', (e) => {
    if (e.target === modalResult) modalResult.style.display = 'none';
    if (e.target === modalRegister) modalRegister.style.display = 'none';
    if (e.target === modalEdit) modalEdit.style.display = 'none';
    if (e.target === modalMarks) modalMarks.style.display = 'none';
  });

  // Initial Load
  loadDashboardData();
});
