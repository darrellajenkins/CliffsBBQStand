import json
import random
import sys
import time
import order
import pmt_sys
from pay import run_payment, pay_result, credit_name
import post
from funcs import clr, bold, blk, italic, red, green, yellow, blue, purple, cyan


today = time.ctime()
today_date = time.strftime('%B %d %Y')
today_time = time.strftime('%I:%M:%S %p')


class Visitors:

    reasons_master_list = [("1", "First time visit"),
                           ("2", "I was here last week"),
                           ("3", "I was here last month"),
                           ("4", "A friend brought me here today"),
                           ("5", "Decided to come with a family member"),
                           ("6", "On a date"),
                           ("7", "I come in every week!"),
                           ("8", "I love Cliff's BBQ Stand!"),
                           ("9", "I am a tourist!"),
                           ("10", "Prefer not to answer")]

    visit_reasons_dict = {  "1": reasons_master_list[0][1], "2": reasons_master_list[1][1], "3": reasons_master_list[2][1],
                            "4": reasons_master_list[3][1], "5": reasons_master_list[4][1], "6": reasons_master_list[5][1],
                            "7": reasons_master_list[6][1], "8": reasons_master_list[7][1], "9": reasons_master_list[8][1], "10": reasons_master_list[9][1]}


    startday_reasons_totals = { "1": [reasons_master_list[0][1], 0], "2": [reasons_master_list[1][1], 0], "3": [reasons_master_list[2][1], 0],
                                "4": [reasons_master_list[3][1], 0], "5": [reasons_master_list[4][1], 0], "6": [reasons_master_list[5][1], 0],
                                "7": [reasons_master_list[6][1], 0], "8": [reasons_master_list[7][1], 0],
                                "9": [reasons_master_list[8][1], 0], "10": [reasons_master_list[9][1], 0]}

    discount_1 = 'please enjoy a $2 discount on your next visit to any of our stores.'
    discount_2 = 'please enjoy a 10% discount on your next visit to any of our stores.'
    discount_3 = 'please enjoy a 15% discount on your next visit to any of our stores.'
    discount_4 = ''  # TBD.
    fr_coupon = 'As a thanks to you both, ' + discount_1
    fr_appreciate = 'We appreciate both of you coming in today to share the fun!'
    fr_rand_select = random.choice([fr_coupon, fr_appreciate, fr_appreciate, fr_appreciate])
    fam_coupon = 'Family members are so important! As a thank you, ' + discount_1
    fam_appreciate = 'We appreciate all of you coming in today to share the fun!'
    fam_rand_select = random.choice([fam_coupon, fam_appreciate, fam_appreciate, fam_appreciate])
    date_coupon = 'As a special thanks to the two of you, ' + discount_2
    date_appreciate = "We appreciate the two of you sharing fun time together at Cliff's BBQ Stand!"
    date_rand_select = random.choice([date_coupon, date_appreciate])
    weekly_coupon = 'Thank you for your customer loyalty, ' + discount_3
    weekly_appreciate = 'You are a valued customer and we truly appreciate your regular visits to our shop! We hope you will bring a friend to share the fun!'
    weekly_rand_select = random.choice([weekly_coupon, weekly_appreciate])

    response_to_reasons = {reasons_master_list[0][1]             : "Thank you for trying out Cliff's BBQ Stand!",
                           reasons_master_list[1][1]             : 'We are so glad you came back!',
                           reasons_master_list[2][1]             : 'Thanks for stopping by again!',
                           reasons_master_list[3][1]             : f'{fr_rand_select}',
                           reasons_master_list[4][1]             : f'{fam_rand_select}',
                           reasons_master_list[5][1]             : f'{date_rand_select}',
                           reasons_master_list[6][1]             : f'{weekly_rand_select}',
                           reasons_master_list[7][1]             : 'We are happy to hear that you enjoy our shop! Bring a friend and share the fun!',
                           reasons_master_list[8][1]             : 'Hope you will enjoy your time visiting the area. Safe travels!',
                           reasons_master_list[9][1]             : 'Thanks for visiting. Please come back!'}

    subscriber_info = []
    non_subscriber_info = []
    reasons_daily_totals = None

    def __init__(self):

        self.companion = False
        self.solo = False
        self.voucher_reason_5 = "Took survey and requested contact."
        self.signed_up = None
        self.reason: str = ""  # Str reason in a short sentence.
        self.reason_num = ""  # Int value captured as a string.
        self.credit_card_name = ""

    def thanks(self):
        tod = ""
        if today_time <= '11:59':
            tod = 'this morning'
        elif today_time <= '17:29':
            tod = 'this afternoon'
        elif today_time <= '19:29':
            tod = 'this evening'
        elif today_time <= '23:59':
            tod = 'tonight'
        return f"\nThank you for visiting Cliff's BBQ Stand {tod}!"

    def comeback(self):
        return f"{purple}We appreciate your business!  Please come back and see us soon!{clr}"

    def ask_who(self):
        print(self.thanks())
        print("\nYou may be able to earn discounts on future visits. May we ask, what brought you in today?\n")
        for who in Visitors.visit_reasons_dict:
            print(f"({who}). {Visitors.visit_reasons_dict[who]}")
        c = 0
        cb = False
        while True:
            ask = input(f"\nPlease enter the {bold}number{clr} of the reason that most closely fits your circumstances: ")
            if not ask.isdigit() or int(ask) < 1 or int(ask) > 10:
                c += 1
                if cb or c >= 2:
                    print(f"{bold}{yellow}Please enter{clr}{red}{bold} a number between 1 and 10.{clr}")
                cb = True
                continue
            else:
                return ask

    def establish_start_day(self):
        try:
            with open(f"reasons_daily_dict_{today_date}.txt") as file_2:
                reasons = json.load(file_2)
                Visitors.reasons_daily_totals = reasons
        except FileNotFoundError:
            self.save_reasons_daily(Visitors.startday_reasons_totals)
            Visitors.reasons_daily_totals = Visitors.startday_reasons_totals
        return Visitors.reasons_daily_totals

    def who(self, ask):
        if ask in Visitors.reasons_daily_totals.keys():
            Visitors.reasons_daily_totals[ask][1] += 1
            self.reason = (Visitors.reasons_daily_totals[ask][0])
            self.reason_num = ask
            self.visit_reason()
            self.print_it(self.acknowledge())
            self.hear_more()
        return

    def acknowledge(self):
        """Acknowledges the reason a visitor came in with an appropriate response based on the Visitor.response_to_reasons dictionary."""
        return f"Thank you! You indicated {bold}{purple}<{self.visit_reason()}>{clr}.\n{Visitors.response_to_reasons[self.visit_reason()]}"

    def print_it(self, item):
        """ Prints any return value/data object used as an argument."""
        print(item)

    def visit_reason(self):
        """Takes the self.reason_num item captured from user in the 'who method' and returns the str words value."""
        if self.reason_num in Visitors.visit_reasons_dict.keys():
            return Visitors.visit_reasons_dict[self.reason_num]
        else:
            return "Unknown reason"

    def discount_given(self):
        """Determines if a coupon was offered to the customer and whether or not they have a companion that will also receive a coupon of their own."""
        if "discount" in Visitors.response_to_reasons[self.visit_reason()]:
            return True

    def solo_or_companion(self):
        if Visitors.reasons_master_list[3][0] == self.reason_num or Visitors.reasons_master_list[4][0]  == self.reason_num or Visitors.reasons_master_list[5][0] == self.reason_num:
            self.companion = True
            return self.companion
        elif Visitors.reasons_master_list[6][0] == self.reason_num:
            self.solo = True
            return self.solo

    def discount_type(self):
        """Returns the specific discount/coupon language to be used in the email to be sent to the customer."""
        if Visitors.discount_1 in Visitors.response_to_reasons[self.visit_reason()]:
            return Visitors.discount_1
        if Visitors.discount_2 in Visitors.response_to_reasons[self.visit_reason()]:
            return Visitors.discount_2
        if Visitors.discount_3 in Visitors.response_to_reasons[self.visit_reason()]:
            return Visitors.discount_3

    def hear_more(self):
        """Navigates user response to whether or not they will hear more about offers and events."""
        cb = False
        print("Cliff's BBQ Stand has the most delicious barbeque and so much fun!")
        while True:
            hear = input(f"\n\t{red}Would you like to be notified about special offers and events? ([Y]es or [N]o to exit) {clr}")
            if hear.lower() == 'y':
                self.write_file(self.email_capture())
                break
            elif hear.lower() == 'n':
                self.signed_up = False
                order_vs_cc = f"Orderer = {self.orderer_name()}.  Credit card holder = {self.credit_card_name}. Email subscriber? = {self.signed_up}"
                non_cust_tup = (self.orderer_name(), order_vs_cc, today, today_date, self.reason, self.order_details)
                Visitors.non_subscriber_info.append(non_cust_tup)
                self.write_file_no_signups(non_cust_tup)
                print(self.comeback())
                return non_cust_tup
            elif hear.lower() != 'y' or hear.lower() != 'n':
                if cb:
                    print(f"{blue}{bold}\tPlease enter{clr} {red}{bold}'Y'{clr} or {red}{bold}'N'{clr}")
                else:
                    cb = True
                continue

    def write_file(self, tup):
        """Saves a file with cust order and contact details."""
        with open(f"{tup[0]}_{today_date}.txt", "a") as file:
            file.write(f"{tup}\n")

    def email_capture(self):
        ques = input(f"Is your name {self.orderer_name()}? ")
        if ques.lower() == 'y':
            email = input(f"Please enter your email address {self.orderer_name()}: ")
            sub_name = self.orderer_name()
            subscriber = "orderer"
        else:
            if self.orderer_name() != self.credit_card_name:
                ques = input(f"Oh, is your name {self.credit_card_name}? ")
                if ques.lower() == 'y':
                    email = input(f"Please enter your email address {self.credit_card_name}: ")
                    sub_name = self.credit_card_name
                    subscriber = "credit card holder"
                else:
                    your_name = input("Please enter your name: ")
                    email = input(f"Please enter your email address {your_name}: ")
                    sub_name = your_name
                    subscriber = "another person"
            else:
                your_name = input("Please enter your name: ")
                email = input(f"Please enter your email address {your_name}: ")
                sub_name = your_name
                subscriber = "another person"
        order_vs_cc = f"Orderer = {self.orderer_name()}.  Credit card holder = {self.credit_card_name}."
        curr_info_tup = (sub_name.title(), order_vs_cc, f"{subscriber = }", email, today, today_time, self.reason, self.order_details)
        Visitors.subscriber_info.append(curr_info_tup)
        return curr_info_tup

    def orderer_name(self):
        return f"{self.order_details[1]} {self.order_details[2]}"

    def save_cust_info(self, daily_customers):
        """Saves cust order data to the group daily custs file including their contact details."""
        with open(f"daily_custs_{today_date}.txt", "a") as file:
            file.write(f"{daily_customers}\n")

    def write_file_no_signups(self, non_cust_tup):
        """Saves a file with cust order data to individual daily file but without contact details."""
        name = f"{non_cust_tup[0]}"
        with open(f"{name}_NonSub_{today_date}.txt", "a") as file:
            file.write(f"{non_cust_tup}\n")

    def save_non_cust_info(self, non_cust_tup):
        """Saves cust order data to the group daily custs file but without adding their contact details."""
        with open(f"daily_custs_{today_date}.txt", "a") as file:
            file.write(f"{non_cust_tup}\n")

    def save_reasons_daily(self, daily_totals):
        """Saves total cust daily reasons for visiting. A report containing this information can be viewed for any day since the software began to be used."""
        with open(f"reasons_daily_dict_{today_date}.txt", "w") as file:
            file.write(json.dumps(daily_totals, indent=4))

    def voucher_reasons(self):
        if self.discount_given():
            return Visitors.response_to_reasons[self.visit_reason()]

    def get_date(self):
        """Gets date from the user and assembles into the format needed by each report method. Allows for 2 or 3 letter abbreviations for the month."""
        months = {'ja': 'January', 'jan': 'January', 'fe': 'February', 'fb': 'February', 'feb': 'February', 'mc': 'March', 'mrc': 'March', 'mar': 'March',
                   'ap': 'April', 'ar': 'April', 'my': 'May', 'may': 'May', 'jn': 'June', 'jne': 'June', 'jun': 'June', 'jul': 'July', 'jly': 'July',
                  'au': 'August', 'ag': 'August', 'se': 'September', 'sp': 'September', 'st': 'September', 'oc': 'October', 'ot': 'October', 'no': 'November',
                  'nv': 'November', 'de': 'December', 'dc': 'December'}
        month = ""

        while True:
            current = input("Press [T] to see today's report or [A] to select a different date: ")
            if current.lower() == 't':
                month = time.strftime('%B')
                day = time.strftime('%d')
                year = time.strftime('%Y')
                return [month, day, year]
            if current.lower() == 'a':
                break
            if current.lower() != 't' and current.lower() != 'a':
                continue
        while True:
            a = input("Month (name or abbreviation): ")
            if len(a) < 2:
                print("Please enter at least 2 letters.")
                continue
            if not a.isalpha():
                print("Please enter at least 2 letters.")
                continue
            elif a.lower() == 'ma' or a.lower() == 'ju':
                print("In this case please enter at least 3 characters.")
                continue
            elif a[0:2].lower() not in months and a[0:3].lower() not in months:
                print("Please make sure you have correctly spelled the month.")
                continue
            elif len(a) >= 2 and a.lower() != 'ma' and a.lower() != 'ju':
                for key, value in months.items():
                    if a[0:2].lower() == key or a[0:3].lower() == key:
                        month = value
                break

        while True:
            two_digit_day = input("Two digit day: ")
            if len(two_digit_day) < 2:
                print("Please enter at least 2 digits.")
                continue
            if not two_digit_day.isdigit():
                print("Please enter at least 2 digits.")
                continue
            if two_digit_day not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                                     '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']:
                print("Please enter a 2 digit day between 01 and 31.")
                continue
            if len(two_digit_day) == 2 and two_digit_day.isdigit():
                break
        day = two_digit_day

        while True:
            four_digit_year = input("Four digit year: ")
            if len(four_digit_year) < 4:
                print("Please enter at least 4 digits.")
                continue
            if not four_digit_year.isdigit():
                print("Please enter at least 4 digits.")
                continue
            if not int(four_digit_year) >= 2024:
                print("Please enter a year 2024 or later.")
                continue
            if len(four_digit_year) == 4 and four_digit_year.isdigit():
                break
        year = four_digit_year

        return [month, day, year]

    def report_custs(self, date):
        """All daily customers report. Format must include the month as a string, 2-digit day, and 4-digit year."""
        month, day, year = date[0], date[1], date[2]
        date_text = f"{month} {day}, {year}"
        try:
            with open(f"daily_custs_{month} {day} {year}.txt", 'r') as file_4:
                contents = file_4.read()
                print(f"{bold}{yellow}\nHere is a list containing details of each customer who placed an order at one of our stores on {date_text}.{clr}")
                print(f"\n{contents}")
            with open(f"daily_custs_{month} {day} {year}.txt", 'r') as file_4a:
                for e, line in enumerate(file_4a, start=1):
                    pass
                print(f"\n{bold}{yellow}There was a total of {e} customer order(s) on {date_text}.{clr}")
        except FileNotFoundError:
            print(f"Report not found for the date requested or no customer orders have been taken or completed on {date_text}.")

    def report_reasons(self, date):
        """Daily reasons overview report."""
        month, day, year = date[0], date[1], date[2]
        date_text = f"{month} {day}, {year}"
        try:
            with open(f"reasons_daily_dict_{month} {day} {year}.txt") as file_5:
                contents = file_5.read()
                print(f"{bold}{purple}\nHere is a summary of the reasons that brought our customers into one of our stores on {date_text}.{clr}\n")
                reasons = json.loads(contents)
                for num, line in reasons.items():
                    if num != '10':
                        print(num + ".","   ", line[0], f"{cyan}", line[1], f"{clr}")
                    else:
                        print(num + ".","  ", line[0], f"{cyan}", line[1], f"{clr}")
        except FileNotFoundError:
            print(f"No customer orders were taken and completed on {date_text}.")

    def report_surveys(self, date):
        """Daily surveys report."""
        month, day, year = date[0], date[1], date[2]
        date_text = f"{month} {day}, {year}"
        try:
            with open(f"surveys_stamped_{month} {day} {year}.txt") as file_6:
                contents = file_6.read()
                print(f"{bold}{cyan}\nHere are all of the customer surveys submitted on {date_text}.{clr}")
                print(f"\n{contents}")
            with open(f"surveys_stamped_{month} {day} {year}.txt", 'r') as file_6a:
                for e, line in enumerate(file_6a, start=1):
                    pass
                print(f"{bold}{cyan}There was a total of {e} customer survey(s) submitted on {date_text}.{clr}")
        except FileNotFoundError:
            print(f"No surveys were taken and completed on {date_text}.")

    def survey_contact_details(self, date):
        """Detailed data on customers who requested to be contacted by a Cliff's BBQ Stand manager in response to their survey."""
        month, day, year = date[0], date[1], date[2]
        date_text = f"{month} {day}, {year}"
        try:
            with open(f"surveys_cust_details_{month} {day} {year}.txt") as file_8:
                contents = file_8.read()
                print(f"{bold}{cyan}\nHere are all details related to customers who asked to be contacted about their survey submitted on {date_text}.{clr}")
                print(f"\n{contents}")
            with open(f"surveys_cust_details_{month} {day} {year}.txt", 'r') as file_8a:
                for e, line in enumerate(file_8a, start=1):
                    pass
                print(f"{bold}{cyan}There was a total of {e} customer(s) who asked to be contacted about their survey(s) submitted on {date_text}.{clr}")
        except FileNotFoundError:
            print(f"No customer has requested contact about their survey completed on {date_text}.")

    def report_daily_vouchers(self, date):
        month, day, year = date[0], date[1], date[2]
        date_text = f"{month} {day}, {year}"
        try:
            with open(f"daily_vouchers_{month} {day} {year}.txt") as file_7:
                contents = file_7.read()
                print(f"{bold}{red}\nHere is a list of all coupons that were issued on {date_text}.{clr}")
                print(f"\n{contents}")
            with open(f"daily_vouchers_{month} {day} {year}.txt", 'r') as file_7a:
                for e, line in enumerate(file_7a, start=1):
                    pass
                print(f"{bold}{cyan}There was a total of {e} separate coupon(s) issued on {date_text}.{clr}")
        except FileNotFoundError:
            print(f"\nNo coupons were issued on {date_text}.")

def new_session():
    """Runs a new order session for a customer regardless of whether or not they have previously visited."""
    while True:
        start = input(f"[B]egin session or [S]ee reports? {bold}B or S{clr}:  ")
        if start.lower() != 'b'.lower() and start.lower() != 's'.lower():
            continue
        else:
            break
    if start.lower() == 'b':
        a = Visitors()
        a.new_cust = order_sys.CustOrder()
        a.order_details = a.new_cust.run_order()
        cc_pay = run_payment()
        paid_or_unpaid = cc_pay[0]
        name_on_credit_card = cc_pay[1]
        pay_result(paid_or_unpaid)
        a.credit_card_name = name_on_credit_card
        print(f"{green}Order is in the name of: {a.orderer_name()}.  Name on credit card: {a.credit_card_name}.{clr}")

        a.establish_start_day()
        a.who(a.ask_who())

        if a.discount_given():
            a_coupon = post_order.Coupon()
            a.solo_or_companion()

            if a.companion:
                x = a_coupon.capture_both_coupon_emails(a.discount_type())
                a_coupon.companion_voucher(x)
                a_coupon.record_daily_vouchers(x[3], x[0], a.voucher_reasons())
                a_coupon.record_daily_vouchers(x[4], x[1], a.voucher_reasons())

            elif a.solo:
                y = a_coupon.capture_coupon_email(a.discount_type())
                a_coupon.cust_voucher(y)
                a_coupon.record_daily_vouchers(y[2], y[0], a.voucher_reasons())

        if Visitors.subscriber_info:
            a.save_cust_info(Visitors.subscriber_info)
            a.save_reasons_daily(Visitors.reasons_daily_totals)
            a_survey = post_order.Survey()
            a_survey.survey_willingness()

            a_survey.get_survey_have_email(Visitors.subscriber_info[0][3])
            v = a_survey.survey_contact(Visitors.subscriber_info[0][3])

            if not a.discount_given():
                a_coupon = post_order.Coupon()

            if v:
                coupon = f"Coupon code: {v[0]}"
                survey_ctc_email = f"Survey contact email: {v[1]}"
                a_coupon.record_daily_vouchers(v[0], v[1], a.voucher_reason_5)
                a_survey.record_survey_details([a_survey.location, a_survey.survey_results, coupon, survey_ctc_email, Visitors.subscriber_info])

        if Visitors.non_subscriber_info:
            a.save_non_cust_info(Visitors.non_subscriber_info)
            a.save_reasons_daily(Visitors.reasons_daily_totals)
            a_survey = post_order.Survey()
            a_survey.survey_willingness()

            get_email = a_survey.get_survey_ask_email()
            vv = a_survey.survey_contact(get_email)

            if not a.discount_given():
                a_coupon = post_order.Coupon()

            if vv:
                coupon = f"Coupon code: {vv[0]}"
                survey_ctc_email = f"Survey contact email: {vv[1]}"
                a_coupon.record_daily_vouchers(vv[0], vv[1], a.voucher_reason_5)
                a_survey.record_survey_details([a_survey.location, a_survey.survey_results, coupon, survey_ctc_email, Visitors.non_subscriber_info])

    if start.lower() == 's':
        a = Visitors()
        same_date = None
        while True:
            reports = input(f"\nReport {yellow}[c]ustomers,{clr} {cyan}[r]easons,{clr} {red}[s]urveys,{clr} {green}[v]ouchers,{clr} {purple} [d]etails on surveys,{clr} [p]revious menu, or [e]xit? ")
            if reports.lower() == 'e':
                sys.exit()
            elif reports.lower() == 'c':
                if same_date:
                    while True:
                        ques = input("Would you like to use the same date as before? [Y]es or [N]o ")
                        if ques.lower() == 'y':
                            same_date = rpt_date
                            a.report_custs(rpt_date)
                            break
                        elif ques.lower() == 'n':
                            rpt_date = a.get_date()
                            a.report_custs(rpt_date)
                            same_date = rpt_date
                            break
                        elif ques.lower() != 'y' or ques.lower() != 'n':
                            continue
                else:
                    rpt_date = a.get_date()
                    a.report_custs(rpt_date)
                    same_date = rpt_date
            elif reports.lower() == 'r':
                if same_date:
                    while True:
                        ques = input("Would you like to use the same date as before? [Y]es or [N]o ")
                        if ques.lower() == 'y':
                            same_date = rpt_date
                            a.report_reasons(rpt_date)
                            break
                        elif ques.lower() == 'n':
                            rpt_date = a.get_date()
                            a.report_reasons(rpt_date)
                            same_date = rpt_date
                            break
                        elif ques.lower() != 'y' or ques.lower() != 'n':
                            continue
                else:
                    rpt_date = a.get_date()
                    a.report_reasons(rpt_date)
                    same_date = rpt_date
            elif reports.lower() == 's':
                if same_date:
                    while True:
                        ques = input("Would you like to use the same date as before? [Y]es or [N]o ")
                        if ques.lower() == 'y':
                            same_date = rpt_date
                            a.report_surveys(rpt_date)
                            break
                        elif ques.lower() == 'n':
                            rpt_date = a.get_date()
                            a.report_surveys(rpt_date)
                            same_date = rpt_date
                            break
                        elif ques.lower() != 'y' or ques.lower() != 'n':
                            continue
                else:
                    rpt_date = a.get_date()
                    a.report_surveys(rpt_date)
                    same_date = rpt_date
            elif reports.lower() == 'd':
                if same_date:
                    while True:
                        ques = input("Would you like to use the same date as before? [Y]es or [N]o ")
                        if ques.lower() == 'y':
                            same_date = rpt_date
                            a.survey_contact_details(rpt_date)
                            break
                        elif ques.lower() == 'n':
                            rpt_date = a.get_date()
                            a.survey_contact_details(rpt_date)
                            same_date = rpt_date
                            break
                        elif ques.lower() != 'y' or ques.lower() != 'n':
                            continue
                else:
                    rpt_date = a.get_date()
                    a.survey_contact_details(rpt_date)
                    same_date = rpt_date
            elif reports.lower() == 'v':
                if same_date:
                    while True:
                        ques = input("Would you like to use the same date as before? [Y]es or [N]o ")
                        if ques.lower() == 'y':
                            same_date = rpt_date
                            a.report_daily_vouchers(rpt_date)
                            break
                        elif ques.lower() == 'n':
                            rpt_date = a.get_date()
                            a.report_daily_vouchers(rpt_date)
                            same_date = rpt_date
                            break
                        elif ques.lower() != 'y' or ques.lower() != 'n':
                            continue
                else:
                    rpt_date = a.get_date()
                    a.report_daily_vouchers(rpt_date)
                    same_date = rpt_datee
            elif reports.lower() == 'p':
                new_session()
                break
            elif reports.lower() != 'c' or reports.lower() != 'r' or reports.lower() != 's' or reports.lower() != 'v':
                continue


new_session()

