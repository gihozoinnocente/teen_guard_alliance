document.addEventListener("DOMContentLoaded", function() {
    const addCourseForm = document.getElementById("addCourseForm");
    const coursesContainer = document.getElementById("coursesContainer");
    const addCourseBtn = document.getElementById("addCourseBtn");
    const addCourseModal = document.getElementById("addCourseModal");
    const closeModalBtn = document.querySelector(".close");
  
    addCourseBtn.addEventListener("click", function() {
      addCourseModal.style.display = "block";
    });
  
    closeModalBtn.addEventListener("click", function() {
      addCourseModal.style.display = "none";
    });
  
    window.addEventListener("click", function(event) {
      if (event.target == addCourseModal) {
        addCourseModal.style.display = "none";
      }
    });
  
    addCourseForm.addEventListener("submit", function(event) {
      event.preventDefault();
      const formData = new FormData(addCourseForm);
      const courseName = formData.get("courseName");
      const category = formData.get("category");
      const level = formData.get("level");
  
      fetch("http://127.0.0.1:7000/add_course", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ courseName, category, level })
      })
      .then(response => response.json())
      .then(data => {
        alert(data.message);
        addCourseModal.style.display = "none";
        addCourseForm.reset();
        loadCourses();
      })
      .catch(error => {
        console.error("Error adding course:", error);
      });
    });
  
    function loadCourses() {
      fetch("http://127.0.0.1:7000/get_courses")
      .then(response => response.json())
      .then(courses => {
        coursesContainer.innerHTML = ""; // Clear previous content
        const groupedCourses = groupCoursesByCategoryAndLevel(courses);
        for (const category in groupedCourses) {
          const categoryDiv = document.createElement("div");
          categoryDiv.classList.add("categoryBox");
          categoryDiv.innerHTML = `<h3>${category}</h3>`;
          for (const level in groupedCourses[category]) {
            const levelDiv = document.createElement("div");
            levelDiv.classList.add("levelBox");
            levelDiv.innerHTML = `<h4>Level ${level}</h4>`;
            groupedCourses[category][level].forEach(course => {
              const courseBox = document.createElement("div");
              courseBox.classList.add("courseBox");
              courseBox.textContent = course.courseName;
              levelDiv.appendChild(courseBox);
            });
            categoryDiv.appendChild(levelDiv);
          }
          coursesContainer.appendChild(categoryDiv);
        }
      })
      .catch(error => {
        console.error("Error loading courses:", error);
      });
    }
  
    function groupCoursesByCategoryAndLevel(courses) {
      const groupedCourses = {};
      courses.forEach(course => {
        if (!groupedCourses[course.category]) {
          groupedCourses[course.category] = {};
        }
        if (!groupedCourses[course.category][course.level]) {
          groupedCourses[course.category][course.level] = [];
        }
        groupedCourses[course.category][course.level].push(course);
      });
      return groupedCourses;
    }
  
    // Load courses when the page is loaded
    loadCourses();
  });
