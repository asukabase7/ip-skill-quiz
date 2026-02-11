(function () {
  "use strict";

  const startScreen = document.getElementById("start-screen");
  const quizScreen = document.getElementById("quiz-screen");
  const resultScreen = document.getElementById("result-screen");
  const btnStartAll = document.getElementById("btn-start-all");
  const btnPastExam = document.getElementById("btn-past-exam");
  const btnAiExam = document.getElementById("btn-ai-exam");
  const reviewBtn = document.getElementById("review-btn");
  const btnStartFiltered = document.getElementById("btn-start-filtered");
  const filterExam = document.getElementById("filter-exam");
  const filterCategory = document.getElementById("filter-category");
  const quizExamTypeBadge = document.getElementById("quiz-exam-type-badge");
  const quizProgress = document.getElementById("quiz-progress");
  const quizCategory = document.getElementById("quiz-category");
  const scenarioBox = document.getElementById("scenario-box");
  const questionText = document.getElementById("question-text");
  const optionsList = document.getElementById("options");
  const resultArea = document.getElementById("result-area");
  const resultMessage = document.getElementById("result-message");
  const explanationEl = document.getElementById("explanation");
  const btnNext = document.getElementById("btn-next");
  const scoreSummary = document.getElementById("score-summary");
  const resultTitleBadge = document.getElementById("result-title-badge");
  const chartContainer = document.getElementById("chart-container");
  const statsChartEl = document.getElementById("statsChart");
  const comboDisplay = document.getElementById("combo-display");
  const btnHomeFromQuiz = document.getElementById("btn-home-from-quiz");
  const btnRetry = document.getElementById("btn-retry");

  const LABELS = { option_a: "ア", option_b: "イ", option_c: "ウ", option_d: "エ" };
  let allQuestions = [];
  let currentList = [];
  let currentIndex = 0;
  let correctCount = 0;
  let answered = false;
  var sessionResults = [];
  var streakCount = 0;
  var statsChartInstance = null;

  function showScreen(screen) {
    [startScreen, quizScreen, resultScreen].forEach(function (el) {
      el.classList.toggle("active", el === screen);
    });
  }

  function fetchQuestions(params) {
    const qs = new URLSearchParams(params).toString();
    return fetch("/api/questions" + (qs ? "?" + qs : "")).then(function (r) {
      if (!r.ok) throw new Error("fetch failed");
      return r.json();
    });
  }

  function recordAnswer(questionId, isCorrect) {
    fetch("/api/record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: questionId, is_correct: isCorrect }),
    }).catch(function () {});
  }

  function loadFilters() {
    return fetchQuestions().then(function (list) {
      const categories = [...new Set(list.map(function (q) { return q.category; }))].filter(Boolean).sort();
      filterCategory.innerHTML = '<option value="">すべて</option>' +
        categories.map(function (c) { return '<option value="' + escapeHtml(c) + '">' + escapeHtml(c) + "</option>"; }).join("");
      allQuestions = list;
      updateReviewButtonVisibility();
    });
  }

  /** 復習データが1件以上あるときだけ「これまでの復習」ボタンを表示する。トップ表示・戻ったときに呼ぶ。 */
  function updateReviewButtonVisibility() {
    fetchQuestions({ mode: "review" }).then(function (list) {
      reviewBtn.hidden = list.length === 0;
    }).catch(function () {
      reviewBtn.hidden = false;
    });
  }

  function escapeHtml(s) {
    if (s == null) return "";
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function startQuiz(list) {
    currentList = list.length ? shuffle(list) : shuffle(allQuestions.slice());
    currentIndex = 0;
    correctCount = 0;
    sessionResults = [];
    streakCount = 0;
    if (currentList.length === 0) {
      alert("問題がありません。");
      return;
    }
    showScreen(quizScreen);
    showQuestion();
  }

  function showQuestion() {
    answered = false;
    resultArea.hidden = true;
    comboDisplay.hidden = true;
    comboDisplay.className = "combo-display";
    const q = currentList[currentIndex];
    const num = currentIndex + 1;
    const total = currentList.length;

    quizProgress.textContent = num + " / " + total;
    if (q.exam_type === "AI模擬") {
      quizExamTypeBadge.textContent = "AI模擬";
      quizExamTypeBadge.hidden = false;
    } else {
      quizExamTypeBadge.hidden = true;
    }
    quizCategory.textContent = q.category;

    if (q.scenario && q.scenario.trim()) {
      scenarioBox.textContent = q.scenario;
      scenarioBox.hidden = false;
    } else {
      scenarioBox.hidden = true;
    }

    questionText.textContent = q.question_text;

    optionsList.innerHTML = "";
    ["option_a", "option_b", "option_c", "option_d"].forEach(function (key) {
      const label = LABELS[key];
      const text = q[key];
      if (text == null || text === "") return;
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "option";
      btn.setAttribute("data-answer", label);
      btn.setAttribute("data-key", key);
      btn.innerHTML = "<span class=\"option-label\">" + label + ".</span>" + escapeHtml(text);
      btn.addEventListener("click", function () { onSelect(btn, q); });
      li.appendChild(btn);
      optionsList.appendChild(li);
    });
  }

  function onSelect(btn, q) {
    if (answered) return;
    answered = true;
    const selected = btn.getAttribute("data-answer");

    fetch("/api/check/" + q.id + "?answer=" + encodeURIComponent(selected))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        const isCorrect = data.is_correct;
        if (isCorrect) {
          correctCount++;
          streakCount++;
        } else {
          streakCount = 0;
        }
        sessionResults.push({ category: q.category || "その他", isCorrect: isCorrect });
        recordAnswer(q.id, isCorrect);

        document.querySelectorAll(".option").forEach(function (el) {
          el.disabled = true;
          const ans = el.getAttribute("data-answer");
          if (ans === data.correct_answer) el.classList.add("correct");
          else if (ans === selected && !isCorrect) el.classList.add("wrong");
        });

        if (streakCount >= 2) {
          comboDisplay.textContent = streakCount + "連勝！\uD83D\uDD25";
          comboDisplay.hidden = false;
          comboDisplay.className = "combo-display combo-" + Math.min(streakCount, 10);
        } else {
          comboDisplay.hidden = true;
        }

        resultArea.hidden = false;
        resultMessage.textContent = isCorrect ? "正解です。" : "不正解です。正解は「" + data.correct_answer + "」です。";
        resultMessage.className = "result-message " + (isCorrect ? "correct" : "wrong");
        explanationEl.textContent = data.explanation || "";
      })
      .catch(function () {
        streakCount = 0;
        comboDisplay.hidden = true;
        resultArea.hidden = false;
        resultMessage.textContent = "判定の取得に失敗しました。";
        resultMessage.className = "result-message wrong";
        explanationEl.textContent = "";
      });
  }

  function getTitle(rate) {
    if (rate >= 1) return "知財の神";
    if (rate >= 0.8) return "知財エキスパート";
    return "知財の卵";
  }

  function buildCategoryStats() {
    var byCat = {};
    sessionResults.forEach(function (r) {
      var c = r.category;
      if (!byCat[c]) byCat[c] = { total: 0, correct: 0 };
      byCat[c].total++;
      if (r.isCorrect) byCat[c].correct++;
    });
    var labels = Object.keys(byCat).sort();
    var data = labels.map(function (cat) {
      var t = byCat[cat].total;
      var c = byCat[cat].correct;
      return t > 0 ? Math.round((c / t) * 100) : 0;
    });
    return { labels: labels, data: data };
  }

  function drawRadarChart() {
    if (statsChartInstance) {
      statsChartInstance.destroy();
      statsChartInstance = null;
    }
    var stats = buildCategoryStats();
    if (stats.labels.length === 0) {
      chartContainer.style.display = "none";
      return;
    }
    chartContainer.style.display = "block";
    var ctx = statsChartEl.getContext("2d");
    statsChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: stats.labels,
        datasets: [{
          label: "正答率（%）",
          data: stats.data,
          backgroundColor: "rgba(44, 82, 130, 0.2)",
          borderColor: "rgba(44, 82, 130, 0.8)",
          pointBackgroundColor: "rgba(44, 82, 130, 1)",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "rgba(44, 82, 130, 1)",
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0,
            max: 100,
            ticks: { stepSize: 25 },
          },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  }

  function nextQuestion() {
    currentIndex++;
    if (currentIndex >= currentList.length) {
      showScreen(resultScreen);
      var total = currentList.length;
      scoreSummary.textContent = total + " 問中 " + correctCount + " 問正解でした。";
      var rate = total > 0 ? correctCount / total : 0;
      resultTitleBadge.textContent = getTitle(rate);
      resultTitleBadge.className = "result-title-badge title-" + (rate >= 1 ? "god" : rate >= 0.8 ? "expert" : "egg");
      drawRadarChart();
      return;
    }
    showQuestion();
  }

  btnStartAll.addEventListener("click", function () {
    startQuiz(allQuestions);
  });

  btnPastExam.addEventListener("click", function () {
    fetchQuestions({ exam_series: "past" }).then(function (list) {
      if (list.length === 0) {
        alert("過去問がありません。");
        return;
      }
      startQuiz(list);
    }).catch(function () {
      alert("問題の取得に失敗しました。");
    });
  });

  btnAiExam.addEventListener("click", function () {
    fetchQuestions({ exam_series: "ai" }).then(function (list) {
      if (list.length === 0) {
        alert("AI模擬問題がありません。");
        return;
      }
      startQuiz(list);
    }).catch(function () {
      alert("問題の取得に失敗しました。");
    });
  });

  reviewBtn.addEventListener("click", function () {
    fetchQuestions({ mode: "review" }).then(function (list) {
      if (list.length === 0) {
        alert("復習する問題はありません！完璧です！");
        return;
      }
      startQuiz(list);
    }).catch(function () {
      alert("復習問題の取得に失敗しました。");
    });
  });

  btnStartFiltered.addEventListener("click", function () {
    const examSeries = filterExam.value.trim();
    const category = filterCategory.value.trim();
    const params = {};
    if (examSeries) params.exam_series = examSeries;
    if (category) params.category = category;
    fetchQuestions(params).then(function (list) {
      startQuiz(list);
    });
  });

  btnNext.addEventListener("click", nextQuestion);

  btnHomeFromQuiz.addEventListener("click", function () {
    if (!confirm("クイズを中断してホームに戻りますか？")) return;
    currentList = [];
    currentIndex = 0;
    correctCount = 0;
    sessionResults = [];
    streakCount = 0;
    showScreen(startScreen);
    updateReviewButtonVisibility();
  });

  btnRetry.addEventListener("click", function () {
    if (statsChartInstance) {
      statsChartInstance.destroy();
      statsChartInstance = null;
    }
    showScreen(startScreen);
    updateReviewButtonVisibility();
  });

  reviewBtn.hidden = true;

  loadFilters().then(function () {
    if (allQuestions.length > 0) {
      btnStartAll.disabled = false;
    }
  }).catch(function () {
    alert("問題の読み込みに失敗しました。");
    reviewBtn.hidden = false;
  });
})();
