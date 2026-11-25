export type User = {
  id: number
  telegram_id: number
  username: string | null
  first_name: string | null
  last_name: string | null
  photo_url: string | null
  is_admin: boolean
  created_at: string
}

export type UserProfile = {
  english_level: string
  total_xp: number
  level: number
  words_learned: number
  lessons_completed: number
  current_lesson_id: number | null
  is_premium: boolean
  premium_until: string | null
  onboarding_completed: boolean
  xp_to_next_level: number
}

export type UserSettings = {
  notifications_enabled: boolean
  reminder_hour: number
  timezone: string
  theme: string
}

export type AuthResponse = {
  access_token: string
  token_type: string
  user: User
}

export type Hearts = {
  count: number
  max_count: number
  next_regen_at: string | null
  seconds_to_next: number | null
}

export type Streak = {
  current_streak: number
  longest_streak: number
  last_activity_date: string | null
  total_active_days: number
}

export type Profile = {
  user: User
  profile: UserProfile
  hearts: Hearts
  streak: Streak
  settings: UserSettings
}

export type Course = {
  id: number
  slug: string
  title: string
  description: string | null
  level: string
  is_premium: boolean
  theme: string | null
  order_index: number
  total_lessons: number
  completed_lessons: number
}

export type Lesson = {
  id: number
  course_id: number
  number: number
  title: string
  description: string | null
  level: string
  theme: string | null
  is_premium: boolean
  xp_reward: number
  status: string | null
}

export type Exercise = {
  id: number
  type: string  // study_card | multiple_choice | translate_en_ru | translate_ru_en | fill_blank | arrange | comprehension
  question: string
  data: Record<string, any>
  xp_reward: number
  order_index: number
}

export type StudyWord = {
  english: string
  russian: string
  transcription: string | null
  example_en: string | null
  example_ru: string | null
}

export type LessonDetail = {
  lesson: Lesson
  exercises: Exercise[]
}

export type AnswerResult = {
  is_correct: boolean
  correct_answer: string | null
  explanation: string | null
  xp_awarded: number
  hearts_remaining: number | null
  lesson_completed: boolean
}

export type Word = {
  id: number
  english: string
  russian: string
  transcription: string | null
  example_en: string | null
  example_ru: string | null
  image_url: string | null
  level: string
  theme: string | null
}

export type UserWord = {
  id: number
  word: Word
  status: string
  next_review_at: string | null
  times_correct: number
  times_wrong: number
}

export type VocabularyStats = {
  total: number
  new: number
  learning: number
  known: number
  due_for_review: number
}

export type League = {
  id: number
  slug: string
  name: string
  tier: number
}

export type LeagueParticipant = {
  id: number
  name: string
  avatar: string | null
  weekly_xp: number
  position: number | null
  is_bot: boolean
  is_user: boolean
}

export type LeagueStatus = {
  league: League
  season_end_at: string
  seconds_to_end: number
  user_position: number | null
  user_weekly_xp: number
  promotion_zone: number
  demotion_zone: number
  participants: LeagueParticipant[]
}

export type PremiumPlan = {
  id: string
  title: string
  stars: number
  duration_days: number
  description: string
  best_value: boolean
}

export type PremiumStatus = {
  is_premium: boolean
  premium_until: string | null
  plan: string | null
}

export type Expression =
  | 'happy'
  | 'sad'
  | 'surprised'
  | 'tired'
  | 'celebrate'
  | 'encourage'
  | 'correct'
  | 'wrong'